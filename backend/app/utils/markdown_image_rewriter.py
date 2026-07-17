import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def extract_markdown_images(markdown_content: str) -> List[Tuple[str, str]]:
    """
    Extract all image references from markdown content.
    Returns a list of tuples: (full_match, image_url)
    
    Matches patterns like:
    - ![alt text](image.png)
    - ![alt](./images/pic.jpg)
    - ![](http://example.com/image.png)
    """
    # Pattern to match markdown images: ![alt](url)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    matches = re.finditer(pattern, markdown_content)
    
    results = []
    for match in matches:
        full_match = match.group(0)  # The entire ![alt](url)
        alt_text = match.group(1)     # The alt text
        image_url = match.group(2)    # The URL/path
        results.append((full_match, image_url, alt_text))
    
    return results


def is_external_url(url: str) -> bool:
    """Check if a URL is external (http/https)."""
    return url.startswith(('http://', 'https://'))


def rewrite_markdown_image_urls(markdown_content: str, course_id: int) -> Tuple[str, List[str]]:
    """
    Rewrite local image references in markdown to use the course API endpoint.
    External URLs (http/https) are left unchanged.
    
    Args:
        markdown_content: The markdown content to process
        course_id: The ID of the course
        
    Returns:
        Tuple of (rewritten_markdown, list_of_referenced_filenames)
        
    Example transformations:
        ![alt](image.png) -> ![alt](/api/course/{course_id}/images/image.png)
        ![alt](./images/pic.jpg) -> ![alt](/api/course/{course_id}/images/pic.jpg)
        ![alt](http://example.com/img.png) -> unchanged (external URL)
    """
    referenced_files = []
    rewritten_content = markdown_content
    
    # Extract all image references
    images = extract_markdown_images(markdown_content)
    
    for full_match, image_url, alt_text in images:
        # Skip external URLs
        if is_external_url(image_url):
            logger.info(f"Skipping external URL: {image_url}")
            continue
        
        # Extract just the filename from the path
        # Remove leading ./ or / and get the last part
        image_url_clean = image_url.lstrip('./')
        filename = image_url_clean.split('/')[-1]
        
        # Build the new URL
        new_url = f"/api/course/{course_id}/images/{filename}"
        
        # Create the new markdown image syntax
        new_match = f"![{alt_text}]({new_url})"
        
        # Replace in content
        rewritten_content = rewritten_content.replace(full_match, new_match)
        
        # Track the filename
        if filename not in referenced_files:
            referenced_files.append(filename)
        
        logger.info(f"Rewrote image reference: {image_url} -> {new_url}")
    
    return rewritten_content, referenced_files


def validate_image_references(
    markdown_content: str,
    course_id: int,
    available_images: List[str]
) -> List[str]:
    """
    Validate that all local image references in markdown exist in the course's uploaded images.
    
    Args:
        markdown_content: The markdown content to validate
        course_id: The ID of the course
        available_images: List of stored_filenames available for this course
        
    Returns:
        List of missing image filenames
    """
    _, referenced_files = rewrite_markdown_image_urls(markdown_content, course_id)
    
    missing_images = []
    for filename in referenced_files:
        if filename not in available_images:
            missing_images.append(filename)
    
    if missing_images:
        logger.warning(f"Missing images for course {course_id}: {missing_images}")
    
    return missing_images


def get_image_filename_from_url(url: str) -> str:
    """
    Extract the filename from an image URL.
    
    Examples:
        /api/courses/123/images/photo.png -> photo.png
        ./images/pic.jpg -> pic.jpg
        photo.png -> photo.png
    """
    return url.split('/')[-1]
