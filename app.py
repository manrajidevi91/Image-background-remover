import cv2
import numpy as np
import os
from sklearn.cluster import KMeans

def clean_image(image):
    """Removes light watermarks and smoothes colors while preserving edges."""
    # 1. Increase contrast to push light watermarks/background to pure white
    # Anything lighter than ~220 will likely become 255
    alpha = 1.3  # Contrast control
    beta = -40   # Brightness control
    cleaned = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    # 2. Apply bilateral filter to remove noise and smooth gradients
    # This keeps edges sharp which is critical for diagrams/text
    cleaned = cv2.bilateralFilter(cleaned, 9, 75, 75)
    
    return cleaned

def remove_background(image):
    """Detects background (white/light areas) for transparency mask."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Threshold to detect background (assuming whitened via clean_image)
    _, mask = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY_INV)
    
    # Clean up mask edges
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask

def convert_to_distinct_grayscale(image, k=5):
    """Clusters colors and maps them to distinct grayscale intensities."""
    # Reshape image for clustering
    h, w, _ = image.shape
    pixels = image.reshape((-1, 3)).astype(np.float32)
    
    # Subsample for faster KMeans
    sample_size = min(20000, len(pixels))
    sample_pixels = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
    
    # Apply KMeans to find dominant colors
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=1)
    kmeans.fit(sample_pixels)
    
    # Sort centers by luminance (Y' = 0.299R + 0.587G + 0.114B)
    centers = kmeans.cluster_centers_
    # Note: OpenCV is BGR
    luminance = 0.114 * centers[:, 0] + 0.587 * centers[:, 1] + 0.299 * centers[:, 2]
    sorted_indices = np.argsort(luminance)
    
    # Create target grayscale levels (ranging from dark to light)
    gray_levels = np.linspace(40, 220, k).astype(int)
    
    # Map cluster labels to gray levels
    label_to_gray = np.zeros(k, dtype=np.uint8)
    for i, idx in enumerate(sorted_indices):
        label_to_gray[idx] = gray_levels[i]
    
    # Predict labels for all pixels and map to gray
    labels = kmeans.predict(pixels)
    gray_flat = label_to_gray[labels]
    
    # Reshape to image and stack to 3-channel BGR
    gray_image = np.stack([gray_flat] * 3, axis=-1).reshape((h, w, 3))
    
    return gray_image

def make_transparent(image, mask):
    """Adds the alpha channel based on the background mask."""
    b, g, r = cv2.split(image)
    rgba = cv2.merge([b, g, r, mask])
    return rgba

def process_image(input_path, output_path):
    """Complete pipeline to clean, quantize, and remove background from images."""
    # Load image
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not read image at {input_path}")
    
    # Step 1: Clean image (Watermark removal + smoothing)
    cleaned = clean_image(image)
    
    # Step 2: Detect background mask from cleaned image
    mask = remove_background(cleaned)
    
    # Step 3: Convert to grayscale with distinct shades (on original-ish cleaned image)
    # We use the cleaned image so that clustering isn't confused by background noise
    gray_image = convert_to_distinct_grayscale(cleaned, k=5)
    
    # Step 4: Combine gray image with background mask
    # We apply a slight softening to the mask to avoid ultra-hard edges
    mask_soft = cv2.GaussianBlur(mask, (3, 3), 0)
    final_image = make_transparent(gray_image, mask_soft)
    
    # Save output
    cv2.imwrite(output_path, final_image)
    print("Processed image saved at:", output_path)


# Main execution block for batch processing
if __name__ == "__main__":
    TEST_DIR = "Test"
    OUTPUT_DIR = "Output"
    
    # Ensure folders exist
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
        print(f"Created {TEST_DIR} folder. Add images there to process.")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Supported image extensions
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    
    # List all image files in the Test folder
    files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(valid_extensions)]
    
    if not files:
        print(f"No images found in '{TEST_DIR}' folder.")
    else:
        print(f"Found {len(files)} image(s) in '{TEST_DIR}'. Starting batch processing...")
        for filename in files:
            input_path = os.path.join(TEST_DIR, filename)
            # Save as .png in Output folder to preserve transparency
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            try:
                process_image(input_path, output_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        print(f"Finished! Processed results are in '{OUTPUT_DIR}'.")