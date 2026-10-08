// frontend/src/components/atoms/BrandLogo/BrandLogo.tsx

// import gaiaLogo from "../../../assets/logos/GAIA-Logo.png";
import kikoLogo from "../../../assets/logos/KIKO-Logo.png";
import "./BrandLogo.css";

type BrandLogoProps = {
  variant?: "sidebar" | "auth" | "compact";
};

export function BrandLogo({ variant = "sidebar" }: BrandLogoProps) {
  return (
    <div className={`brand-logo brand-logo--${variant}`}>
      <img src={kikoLogo} alt="GAIA Lab" className="brand-logo__image" />
    </div>
  );
}
