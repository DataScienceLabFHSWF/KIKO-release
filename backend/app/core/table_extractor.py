import numpy as np, cv2 as cv, logging
from PIL import Image
from .ocr_manager import OCRManager

logger = logging.getLogger(__name__)

class TableExtractor:
    """Extract tables from documents using advanced computer vision."""
    
    def __init__(self, config):
        print("ℹ️ Initializing TableExtractor with advanced CV techniques...")
        self.config = config
    
    async def detect_tables(self, image):
        """Detect tables in image using advanced CV techniques."""
        if not self.config.get("flags").get('is_cv2_available'):
            print("⚠️ OpenCV is not available. Table detection will be skipped.")
            return []
            
        try:
            if isinstance(image, Image.Image):
                if image.mode != "RGB":
                    image = image.convert("RGB")
                img_np = np.asarray(image)
            else:
                img_np = image
            
            # Convert to grayscale
            if len(img_np.shape) == 3:
                gray = cv.cvtColor(img_np, cv.COLOR_RGB2GRAY)
            else:
                gray = img_np
            
            # Advanced table detection
            tables = []
            
            # Method 1: Line-based detection
            tables.extend(await self._detect_tables_by_lines(gray))
            
            # Method 2: Contour-based detection
            tables.extend(await self._detect_tables_by_contours(gray))
            
            # Remove duplicates and filter
            tables = await self._filter_and_merge_tables(tables)

            print(f"ℹ️ Detected {len(tables)} potential tables.")            
            return tables
            
        except Exception as e:
            print(f"❌ Error during table detection: {str(e)}")
            return []
    
    async def _detect_tables_by_lines(self, gray):
        """Detect tables using line analysis."""
        try:
            _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (40, 1))
            vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=1)
            vertical_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, vertical_kernel, iterations=1)
            
            # Combine lines
            table_mesh = cv.add(horizontal_lines, vertical_lines)
            
            # Find table regions
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
            table_mesh = cv.dilate(table_mesh, kernel, iterations=2)
            
            contours, _ = cv.findContours(table_mesh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            tables = []
            for contour in contours:
                x, y, w, h = cv.boundingRect(contour)
                
                if w < 100 or h < 100:
                    continue
                
                aspect_ratio = max(w, h) / min(w, h)
                if aspect_ratio > 15:
                    continue
                
                tables.append([x, y, x+w, y+h])
            
            print(f"ℹ️ Detected {len(tables)} tables using line analysis.")
            return tables
            
        except Exception as e:
            print(f"❌ Error during line-based table detection: {str(e)}")
            return []
    
    async def _detect_tables_by_contours(self, gray):
        """Detect tables using contour analysis."""
        try:
            # Apply adaptive thresholding
            thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            tables = []
            for contour in contours:
                area = cv.contourArea(contour)
                if area < 1000:  # Filter small contours
                    continue
                
                # Check if contour is rectangular
                epsilon = 0.02 * cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, epsilon, True)
                
                if len(approx) >= 4:  # At least quadrilateral
                    x, y, w, h = cv.boundingRect(contour)
                    
                    # Filter by size and aspect ratio
                    if w > 100 and h > 100:
                        aspect_ratio = max(w, h) / min(w, h)
                        if aspect_ratio < 10:  # Not too elongated
                            tables.append([x, y, x+w, y+h])
            
            print(f"ℹ️ Detected {len(tables)} tables using contour analysis.")
            return tables
            
        except Exception as e:
            print(f"❌ Error during contour-based table detection: {str(e)}")
            return []
    
    async def _filter_and_merge_tables(self, tables):
        """Filter and merge overlapping table detections."""
        if not tables:
            print("⚠️ No tables detected to filter or merge.")
            return []
        
        # Remove duplicates and merge overlapping
        merged_tables = []
        
        for table in tables:
            x1, y1, x2, y2 = table
            
            # Check if this table overlaps significantly with existing ones
            overlap_found = False
            for i, existing in enumerate(merged_tables):
                ex1, ey1, ex2, ey2 = existing
                
                # Calculate overlap
                overlap_x = max(0, min(x2, ex2) - max(x1, ex1))
                overlap_y = max(0, min(y2, ey2) - max(y1, ey1))
                overlap_area = overlap_x * overlap_y
                
                table_area = (x2 - x1) * (y2 - y1)
                existing_area = (ex2 - ex1) * (ey2 - ey1)
                
                # If overlap is significant, merge
                if overlap_area > 0.5 * min(table_area, existing_area):
                    # Merge bounding boxes
                    merged_tables[i] = [
                        min(x1, ex1), min(y1, ey1),
                        max(x2, ex2), max(y2, ey2)
                    ]
                    overlap_found = True
                    break
            
            if not overlap_found:
                merged_tables.append(table)
        print(f"✅ Merged to {len(merged_tables)} unique table detections.")
        return merged_tables
    
    async def extract_table_structure(self, image, table_bbox):
        """Extract table structure using advanced analysis."""
        try:
            if isinstance(image, Image.Image):
                table_img = image.crop(table_bbox)
                table_np = np.asarray(table_img)
            else:
                x0, y0, x1, y1 = [int(coord) for coord in table_bbox]
                table_np = image[y0:y1, x0:x1]
                table_img = Image.fromarray(table_np)
            
            # Use state-of-the-art OCR for table content extraction
            ocr_manager = OCRManager(self.config)
            ocr_engine = await ocr_manager.get_best_ocr_engine("table", "auto")
            
            # Extract text from entire table
            table_text = ocr_engine(table_img)
            
            # Also try to detect structure
            structure = await self._analyze_table_structure(table_np)

            print(f"✅ Extracted table structure: {structure}")
            
            return {
                "rows": structure.get("rows", 1),
                "columns": structure.get("columns", 1),
                "text": table_text,
                "bbox": table_bbox,
                "structure": structure
            }
        except Exception as e:
            print(f"❌ Error extracting table structure: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_table_structure(self, table_image):
        """Analyze table structure to determine rows and columns."""
        try:
            if not self.config.get("flags").get('is_cv2_available'):
                print("⚠️ OpenCV is not available. Table structure analysis will be skipped.")
                return {"rows": 1, "columns": 1}
            
            gray = cv.cvtColor(table_image, cv.COLOR_RGB2GRAY) if len(table_image.shape) == 3 else table_image
            
            # Detect horizontal and vertical lines
            _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)
            
            h, w = gray.shape
            horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (w // 10, 1))
            vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, h // 10))
            
            horizontal_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=1)
            vertical_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, vertical_kernel, iterations=1)
            
            # Find line positions
            horizontal_projection = np.sum(horizontal_lines, axis=1)
            vertical_projection = np.sum(vertical_lines, axis=0)
            
            # Count significant peaks (lines)
            row_count = len(await self._find_peaks(horizontal_projection))
            col_count = len(await self._find_peaks(vertical_projection))
            
            # Ensure minimum counts
            row_count = max(1, row_count - 1)  # Lines define rows between them
            col_count = max(1, col_count - 1)  # Lines define columns between them
            
            print(f"ℹ️ Detected {row_count} rows and {col_count} columns in table structure.")
            return {
                "rows": row_count,
                "columns": col_count,
                "horizontal_lines": len(await self._find_peaks(horizontal_projection)),
                "vertical_lines": len(await self._find_peaks(vertical_projection))
            }
            
        except Exception as e:
            print(f"❌ Error analyzing table structure: {str(e)}")
            return {"rows": 1, "columns": 1}
    
    async def _find_peaks(self, projection, min_height=None, min_distance=10):
        """Find peaks in projection profile."""
        if min_height is None:
            min_height = np.max(projection) * 0.3
        
        peaks = []
        for i in range(1, len(projection) - 1):
            if (projection[i] > projection[i-1] and 
                projection[i] > projection[i+1] and 
                projection[i] > min_height):
                
                # Check minimum distance from previous peaks
                if not peaks or i - peaks[-1] >= min_distance:
                    peaks.append(i)
        
        print(f"ℹ️ Found {len(peaks)} peaks in projection profile.")
        return peaks
