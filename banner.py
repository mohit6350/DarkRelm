from PIL import Image, ImageFilter
import sys
import os

# More detailed ASCII character set for sharper output (dark to light)
ASCII_CHARS = "@$%#&*+=|;:~-,.' "

def enhance_image(image):
    """Aggressively enhance image for sharper ASCII conversion"""
    image = image.convert('L')
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)  # Stronger edge enhancement
    image = image.filter(ImageFilter.SHARPEN)           # Sharpen twice
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.DETAIL)            # Increase contrast
    return image

def pixels_to_ascii(image, output_width=90, output_height=50):
    """Convert pixel values to ASCII characters with terminal-friendly size"""
    # Resize to terminal-friendly dimensions maintaining 16:9 aspect ratio
    image = image.resize((output_width, output_height), Image.Resampling.LANCZOS)
    pixels = image.getdata()
    char_len = len(ASCII_CHARS)
    return ''.join([ASCII_CHARS[min(int(pixel * char_len / 256), char_len - 1)] for pixel in pixels])

def image_to_ascii(image_path, output_width=90, output_height=50):
    """Convert image to sharp ASCII art optimized for 1920x1080 display"""
    try:
        # Open and process the image
        image = Image.open(image_path)
        
        # Enhance image for maximum sharpness
        image = enhance_image(image)
        
        # Convert to ASCII with terminal-friendly size
        ascii_str = pixels_to_ascii(image, output_width, output_height)
        
        # Format the ASCII art with line breaks
        ascii_art = [ascii_str[i:i + output_width] for i in range(0, len(ascii_str), output_width)]
        return "\n".join(ascii_art)
    
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        print("Example: python script.py myimage.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found")
        sys.exit(1)
    
    ascii_art = image_to_ascii(image_path)
    print(ascii_art)
    print(f"\nOutput size: 90 characters wide x 50 lines tall (16:9 aspect ratio)")

if __name__ == "__main__":
    main()