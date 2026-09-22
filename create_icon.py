from PIL import Image, ImageDraw

# Create 512x512 transparent canvas
img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 1. Extended Yellow Measuring Blade (Bottom Right)
draw.rectangle([140, 370, 460, 430], fill='#f59e0b', outline='#b45309', width=4)
# Ruler tick marks along blade
for x in range(160, 450, 18):
    h = 22 if (x - 160) % 36 == 0 else 12
    draw.line([x, 370, x, 370 + h], fill='#1e293b', width=3)

# 2. Main Casing (Petrie Navy Casing with Gold Ring)
draw.rounded_rectangle([70, 70, 370, 370], radius=70, fill='#3b4876', outline='#1e293b', width=8)
# Outer Rubber Grip Corner Accent
draw.rounded_rectangle([60, 220, 180, 380], radius=40, fill='#1e293b')
draw.rounded_rectangle([70, 70, 370, 370], radius=70, fill=None, outline='#3b4876', width=8)

# 3. Center Reel Badge
draw.ellipse([140, 140, 300, 310], fill='#f59e0b', outline='#b45309', width=6)
draw.ellipse([195, 195, 245, 245], fill='#1e293b')

# 4. Red Thumb-Lock Switch (Top Left)
draw.rounded_rectangle([180, 35, 250, 80], radius=12, fill='#e53e3e', outline='#9b2c2c', width=4)

# 5. Silver Belt Clip (Left Side)
draw.rounded_rectangle([45, 170, 75, 270], radius=8, fill='#cbd5e0', outline='#64748b', width=3)

# Save PNG to assets
img.save('assets/icon.png')
print("Tape measure icon saved to assets/icon.png")