img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
brand_color = '#3b4876'

# 1. Extended Tape Hook
draw.polygon([(390, 160), (425, 30), (445, 78), (415, 170)], fill=brand_color)
draw.polygon([(425, 30), (500, 60), (485, 98), (445, 78)], fill=brand_color)

# 2. Main Teardrop Casing
draw.ellipse([60, 160, 340, 440], fill=brand_color)
draw.polygon([(185, 161), (415, 200), (318, 395)], fill=brand_color)

# 3. Inner White Hub
draw.ellipse([110, 210, 290, 390], fill='#ffffff')

# 4. Center Bold 'P'
draw.rectangle([152, 240, 182, 360], fill=brand_color)
draw.rounded_rectangle([152, 240, 248, 310], radius=25, fill=brand_color)
draw.rounded_rectangle([182, 260, 220, 290], radius=12, fill='#ffffff')

img.save('perfect_p_icon.png')