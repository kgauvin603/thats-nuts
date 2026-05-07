import { useEffect, useState } from 'react';

interface ProductImageCardProps {
  imageUrl?: string | null;
  productName?: string | null;
}

export function ProductImageCard({
  imageUrl,
  productName,
}: ProductImageCardProps) {
  const [hasFailed, setHasFailed] = useState(false);
  const showImage = Boolean(imageUrl) && !hasFailed;

  useEffect(() => {
    setHasFailed(false);
  }, [imageUrl]);

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
        <div aria-label="Product image placeholder" className="product-image-placeholder">
          <span>No product photo available</span>
        </div>
      )}
    </div>
  );
}
