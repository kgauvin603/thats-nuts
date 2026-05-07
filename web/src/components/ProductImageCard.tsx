import { type ReactNode, useState } from 'react';

interface ProductImageCardProps {
  imageUrl?: string | null;
  productName?: string | null;
  placeholderContent?: ReactNode;
}

export function ProductImageCard({
  imageUrl,
  productName,
  placeholderContent,
}: ProductImageCardProps) {
  const [hasFailed, setHasFailed] = useState(false);
  const showImage = Boolean(imageUrl) && !hasFailed;

  return (
    <div className="product-image-card">
      {showImage ? (
        <img
          alt={productName || 'Product image'}
          className="product-image"
          onError={() => setHasFailed(true)}
          src={imageUrl ?? undefined}
        />
      ) : (
        placeholderContent || (
          <div
            aria-label="Product image placeholder"
            className="product-image-placeholder"
          >
            <span>No product photo available</span>
          </div>
        )
      )}
    </div>
  );
}
