from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.graphics.shapes import Circle, Drawing, String
from reportlab.graphics import renderPDF
from datetime import datetime
from io import BytesIO
import os

# Shared color scheme
COMPANY_NAVY = HexColor('#121044')
COMPANY_GOLD = HexColor('#C4A864')
COMPANY_ORANGE = HexColor('#FF9600')
MEDAL_GOLD = HexColor('#FFD700')     # Traditional gold
MEDAL_SILVER = HexColor('#C0C0C0')   # Traditional silver
MEDAL_BRONZE = HexColor('#CD7F32')   # Traditional bronze
MEDAL_GREY = HexColor('#718096')     # Grey for 4th and 5th

def get_header_image():
    """Get the path to the header image with detailed debugging"""
    possible_paths = [
        'assets/pdf_header.png',
        os.path.join(os.path.dirname(__file__), 'assets', 'pdf_header.png')
    ]
    
    print("\nSearching for header image:")
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        print(f"Checking: {abs_path}")
        if os.path.exists(path):
            print(f"Found header image at: {abs_path}")
            try:
                with open(path, 'rb') as f:
                    f.read(1)
                print("File is readable")
                return path
            except Exception as e:
                print(f"File exists but cannot be read: {str(e)}")
    
    print("No readable header image found")
    return None

def create_header_with_image(width):
    """Create a header using the custom image"""
    header_path = get_header_image()
    
    if header_path:
        try:
            header_img = Image(header_path)
            
            # Set the width to match the page width
            aspect_ratio = float(header_img.imageWidth) / float(header_img.imageHeight)
            target_width = width
            target_height = width / aspect_ratio
            
            header_img.drawWidth = target_width
            header_img.drawHeight = target_height
            
            print(f"Header image dimensions: {target_width}x{target_height} points")
            
            return header_img
            
        except Exception as e:
            print(f"Error in create_header_with_image: {str(e)}")
            return Paragraph('Baseball Performance Leaderboards',
                           getSampleStyleSheet()['Title'])
    else:
        return Paragraph('Baseball Performance Leaderboards',
                        getSampleStyleSheet()['Title'])


def get_logo_path():
    """Get the path to the logo file with detailed debugging"""
    possible_paths = [
        'pdf_logo.png',
        'assets/pdf_logo.png',
        os.path.join(os.path.dirname(__file__), 'pdf_logo.png'),
        os.path.join(os.path.dirname(__file__), 'assets', 'pdf_logo.png')
    ]
    
    print("\nSearching for logo files:")
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        print(f"Checking: {abs_path}")
        if os.path.exists(path):
            print(f"Found logo at: {abs_path}")
            # Verify file is readable
            try:
                with open(path, 'rb') as f:
                    f.read(1)
                print("File is readable")
                return path
            except Exception as e:
                print(f"File exists but cannot be read: {str(e)}")
    
    print("No readable logo file found")
    return None


def create_header_with_logo(width, height=1.0*inch):
    """Create a header table with centered logo and text on one line"""
    logo_path = get_logo_path()
    
    if logo_path:
        try:
            logo = Image(logo_path)
            
            # Adjust logo size to be more proportional
            target_height = 72  # Reduced height for one-line layout
            aspect_ratio = float(logo.imageWidth) / float(logo.imageHeight)
            target_width = int(target_height * aspect_ratio)
            
            logo.drawHeight = target_height
            logo.drawWidth = target_width
            
            print(f"Logo dimensions: {logo.drawWidth}x{logo.drawHeight} points")
            
            # Create a single-row table with logo and text side by side
            header_table = Table(
                [[logo, Paragraph(
                    '<para align="center"><font color="#121044" size="24">Baseball Performance Leaderboards</font></para>',
                    getSampleStyleSheet()['Normal']
                )]],
                colWidths=[target_width + 20,  # Logo width plus small padding
                          width - target_width - 20],  # Remaining width for text
                rowHeights=[target_height + 10]  # Slightly taller than logo
            )
            
            # Center everything both horizontally and vertically
            header_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Center horizontally
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Center vertically
                ('LEFTPADDING', (0,0), (-1,-1), 10),  # Even padding
                ('RIGHTPADDING', (0,0), (-1,-1), 10), 
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5)
            ]))
            
            return header_table
            
        except Exception as e:
            print(f"Error in create_header_with_logo: {str(e)}")
            return Paragraph('Baseball Performance Leaderboards',
                           getSampleStyleSheet()['Title'])
    else:
        return Paragraph('Baseball Performance Leaderboards',
                        getSampleStyleSheet()['Title'])
        
        
def create_rank_badge(rank, size=14):
    """Create a circular badge with rank number"""
    d = Drawing(size, size)
    
    # Traditional medal colors
    colors = {
        1: MEDAL_GOLD,    
        2: MEDAL_SILVER,  
        3: MEDAL_BRONZE,  
        4: MEDAL_GREY,    
        5: MEDAL_GREY     
    }
    
    # Create circle
    circle = Circle(size/2, size/2, size/2, fillColor=colors.get(rank))
    d.add(circle)
    
    # Add number
    text_color = black if rank == 1 else white  # Black text only for gold medal
    number = String(size/2, size/2 - 3.5, str(rank),
                   fontSize=8,
                   fillColor=text_color,
                   textAnchor='middle')
    d.add(number)
    
    return d

def create_player_card(player_data, styles):
    """Create a card-like table for a single player"""
    name = player_data['name']
    value = f"{player_data['value']:.1f} {player_data['unit']}"
    rank = player_data['rank']
    ab = player_data.get('total_abs', 0)
    avg = player_data.get('batting_avg', 0)
    slg = player_data.get('slg_pct', 0)
    hr = player_data.get('home_runs', 0)
    
    badge = create_rank_badge(rank)
    
    # More compact card layout
    data = [
        [badge, 
         Paragraph(f"<b>{name}</b>", styles['Normal']), 
         Paragraph(f"<font color='{COMPANY_NAVY.hexval()}'><b>{value}</b></font>", styles['Normal'])],
        ['', f"AB: {ab}  AVG: {avg:.3f}  SLG: {slg:.3f}  HR: {hr}", '']
    ]
    
    # More compact table
    table = Table(data, colWidths=[0.25*inch, 2.25*inch, 1.25*inch], 
                 rowHeights=[0.22*inch, 0.22*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), white),
        ('BOX', (0,0), (-1,-1), 0.5, COMPANY_GOLD),  # Company gold border
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),    # Minimal padding
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    return table

def create_leaderboard_pdf(grad_year, leaderboard_data, start_date=None, end_date=None):
    """Create a single-page PDF document with card-based leaderboards"""
    buffer = BytesIO()
    
    # Set even margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,    # 0.5 inch
        leftMargin=36,     # 0.5 inch
        topMargin=36,      # 0.5 inch
        bottomMargin=36    # 0.5 inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COMPANY_NAVY,
        spaceAfter=0,
        spaceBefore=0,
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=COMPANY_GOLD,
        spaceAfter=8,
        spaceBefore=4,
        alignment=1  # Center alignment
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=COMPANY_NAVY,
        spaceBefore=6,
        spaceAfter=6
    )
    
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COMPANY_GOLD,
        alignment=2,  # Right alignment
        spaceBefore=0,
        spaceAfter=4
    )
    
    elements = []
    
    # Create centered header
    header_table = create_header_with_logo(doc.width)
    elements.append(header_table)
    elements.append(Spacer(1, 12))  # Add space after header
    
    # Add grad year
    elements.append(Paragraph(f"Class of {grad_year}", title_style))
    
    # Add subtitle
    elements.append(Paragraph("Baseball Performance Leaderboards", subtitle_style))
    
    # Add date range
    if start_date and end_date:
        date_range = f"Data from {start_date} to {end_date}"
    else:
        date_range = f"Data as of {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(date_range, date_style))
    elements.append(Spacer(1, 4))
    
    # Create all sections in one table
    sections = []
    metrics = [
        ('max-exit-velocity', 'Max Exit Velocity'),
        ('average-exit-velocity', 'Average Exit Velocity'),
        ('max-distance', 'Max Distance'),
        ('average-distance', 'Average Distance')
    ]
    
    # Generate sections with player cards
    for metric_key, title in metrics:
        section = []
        section.append(Paragraph(title, section_style))
        
        metric_data = leaderboard_data.get(metric_key, {}).get(grad_year, [])
        for player_data in metric_data[:5]:  # Top 5 players
            card = create_player_card(player_data, styles)
            section.append(card)
            section.append(Spacer(1, 2))  # Small space between cards
            
        sections.append(section)
    
    # Create 2x2 grid of sections
    grid_data = [
        [sections[0], sections[1]],  # Top row
        [sections[2], sections[3]]   # Bottom row
    ]
    
    # Create the main layout table
    main_table = Table(
        grid_data,
        colWidths=[4*inch, 4*inch],  # Even split for two columns
        spaceBefore=10
    )
    
    # Style the main table
    main_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),     # Center all content
        ('VALIGN', (0,0), (-1,-1), 'TOP'),       # Align to top
        ('LEFTPADDING', (0,0), (-1,-1), 4),      # Minimal padding
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    elements.append(main_table)
    
    try:
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error building PDF: {str(e)}")
        return None


def create_social_media_image(grad_year, leaderboard_data, start_date=None, end_date=None):
    """Create a social media image for the leaderboard"""
    try:
        # First generate the PDF
        print("Generating PDF...")
        pdf_buffer = create_leaderboard_pdf(grad_year, leaderboard_data, start_date, end_date)
        if not pdf_buffer:
            raise ValueError("PDF buffer is empty")

        print("Converting PDF to image...")
        # Convert PDF to image
        images = convert_from_bytes(
            pdf_buffer.getvalue(),
            dpi=300,  # High DPI for quality
            fmt='png',
            size=(1080, 1080)  # Instagram square format
        )
        
        if not images:
            raise ValueError("No images generated from PDF")
            
        print("Processing image...")
        # Get first page and ensure it's RGB
        first_page = images[0]
        if first_page.mode != 'RGB':
            first_page = first_page.convert('RGB')
        
        # Create new image with white background at target size
        target_size = (1080, 1080)
        new_image = Image.new('RGB', target_size, 'white')
        
        # Calculate position to center the page
        x = (target_size[0] - first_page.size[0]) // 2
        y = (target_size[1] - first_page.size[1]) // 2
        
        # Paste the page onto the new image
        new_image.paste(first_page, (x, y))
        
        print("Saving image...")
        # Save to buffer
        img_buffer = BytesIO()
        new_image.save(img_buffer, format='PNG', quality=95, optimize=True)
        img_buffer.seek(0)
        
        print("Image generation complete")
        return img_buffer
            
    except Exception as e:
        print(f"Error creating social media image: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Create error image
        error_img = Image.new('RGB', (1080, 1080), 'white')
        draw = ImageDraw.Draw(error_img)
        draw.text((540, 540), f"Error generating image: {str(e)}", 
                fill='black', anchor="mm")
        
        error_buffer = BytesIO()
        error_img.save(error_buffer, format='PNG')
        error_buffer.seek(0)
        return error_buffer

class SocialMediaGraphicsGenerator:
    # Professional color scheme
    COLORS = {
        'primary': '#121044',      # Navy blue
        'secondary': '#9B8967',    # Gold
        'accent': '#FF9600',       # Orange
        'background': '#FFFFFF',   # White background
        'text_dark': '#1A202C',    # Dark gray
        'text_light': '#FFFFFF',   # White
        'medal_gold': '#FFD700',   # Gold medal
        'medal_silver': '#C0C0C0', # Silver medal
        'medal_bronze': '#CD7F32', # Bronze medal
        'medal_other': '#718096',  # Other rankings
        'card_bg': '#F8F9FA'       # Light gray card background
    }
    
    def __init__(self):
        """Initialize with custom fonts"""
        try:
            # Use system fonts that are likely to be available
            title_size = 72
            header_size = 48
            subheader_size = 36
            text_size = 24
            
            # For macOS
            if os.path.exists('/System/Library/Fonts/'):
                self.title_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', title_size)
                self.header_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', header_size)
                self.subheader_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', subheader_size)
                self.text_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', text_size)
                self.stats_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', text_size)
            # For Windows
            elif os.path.exists('C:\\Windows\\Fonts\\'):
                self.title_font = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', title_size)
                self.header_font = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', header_size)
                self.subheader_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', subheader_size)
                self.text_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', text_size)
                self.stats_font = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', text_size)
            # Fallback to default
            else:
                self.title_font = ImageFont.load_default()
                self.header_font = ImageFont.load_default()
                self.subheader_font = ImageFont.load_default()
                self.text_font = ImageFont.load_default()
                self.stats_font = ImageFont.load_default()
        except Exception as e:
            print(f"Error loading fonts: {str(e)}")
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.subheader_font = ImageFont.load_default()
            self.text_font = ImageFont.load_default()
            self.stats_font = ImageFont.load_default()

    def _add_decorative_elements(self, draw, width, height):
        """Add decorative design elements"""
        # Add subtle corner accents
        corner_size = int(width * 0.1)  # 10% of width
        line_width = max(3, int(width * 0.003))  # Scale line width with image size
        
        # Top left corner
        draw.line([(0, corner_size), (0, 0), (corner_size, 0)], 
                 fill=self.COLORS['accent'], width=line_width)
        
        # Bottom right corner
        draw.line([(width-corner_size, height), (width, height), (width, height-corner_size)], 
                 fill=self.COLORS['accent'], width=line_width)

    def create_background(self, width, height):
        """Create a professional background with gradient"""
        img = Image.new('RGB', (width, height), self.COLORS['background'])
        draw = ImageDraw.Draw(img)
        
        # Get primary color components
        primary_color = self.COLORS['primary'].lstrip('#')
        r = int(primary_color[:2], 16)
        g = int(primary_color[2:4], 16)
        b = int(primary_color[4:], 16)
        
        # Create subtle gradient background
        for y in range(height):
            alpha = int((y / height) * 10)  # Very subtle gradient
            gradient_color = f'#{r:02x}{g:02x}{b:02x}{alpha:02x}'
            draw.line([(0, y), (width, y)], fill=gradient_color)
        
        # Add decorative elements
        self._add_decorative_elements(draw, width, height)
        
        return img, draw

    def create_rank_badge(self, draw, x, y, rank, size=60):
        """Create a professional-looking rank badge with shadow effect"""
        colors = {
            1: self.COLORS['medal_gold'],
            2: self.COLORS['medal_silver'],
            3: self.COLORS['medal_bronze']
        }
        badge_color = colors.get(rank, self.COLORS['medal_other'])
        
        # Add shadow
        shadow_offset = 3
        draw.ellipse([x+shadow_offset, y+shadow_offset, x+size+shadow_offset, y+size+shadow_offset], 
                    fill='#00000033')
        
        # Main circle
        draw.ellipse([x, y, x+size, y+size], fill=badge_color)
        
        # Add shine effect
        shine_offset = size // 4
        shine_size = size - (shine_offset * 2)
        draw.ellipse([x+shine_offset, y+shine_offset, 
                     x+shine_offset+shine_size, y+shine_offset+shine_size],
                    fill=badge_color, outline='#FFFFFF44', width=2)
        
        # Add rank number
        number_color = 'black' if rank == 1 else 'white'
        text = str(rank)
        font = self.stats_font
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        draw.text((x + (size-text_width)//2, y + (size-text_height)//2),
                 text, fill=number_color, font=font)

    def create_player_card(self, draw, x, y, player_data, width=480, height=120):
        """Create a professional player stat card"""
        try:
            # Add card shadow
            shadow_offset = 4
            draw.rectangle([x+shadow_offset, y+shadow_offset, x+width+shadow_offset, y+height+shadow_offset],
                        fill='#00000022')
            
            # Card background with gradient
            draw.rectangle([x, y, x+width, y+height],
                        fill=self.COLORS['card_bg'], outline=self.COLORS['secondary'], width=2)
            
            # Add rank badge
            badge_size = int(height * 0.5)
            badge_x = x + 15
            badge_y = y + (height - badge_size) // 2
            self.create_rank_badge(draw, badge_x, badge_y, player_data['rank'], badge_size)
            
            # Content area
            content_x = badge_x + badge_size + 20
            
            # Player name (bold)
            name_y = y + 15
            name = str(player_data['name'])  # Ensure name is a string
            draw.text((content_x, name_y), name,
                    fill=self.COLORS['primary'], font=self.header_font)
            
            # School name (smaller, regular font)
            school_y = name_y + 35
            school_text = str(player_data.get('school', ''))  # Ensure school is a string
            if school_text:  # Only draw if school is provided
                draw.text((content_x, school_y), school_text,
                        fill=self.COLORS['secondary'], font=self.text_font)
            
            # Main stat value (large, bold)
            value_text = f"{float(player_data['value']):.1f} {player_data['unit']}"
            draw.text((x + width - 20, y + height//2),
                    value_text, fill=self.COLORS['accent'], 
                    font=self.stats_font, anchor="rm")
            
            # Stats row (compact, clear layout)
            stats_y = y + height - 30
            stats_text = (f"AB: {int(player_data['total_abs'])} | "
                        f"AVG: {float(player_data['batting_avg']):.3f} | "
                        f"SLG: {float(player_data['slg_pct']):.3f} | "
                        f"HR: {int(player_data['home_runs'])}")
            draw.text((content_x, stats_y), stats_text,
                    fill=self.COLORS['text_dark'], font=self.text_font)
        except Exception as e:
            print(f"Error creating player card: {str(e)}")
            # Draw error card
            draw.rectangle([x, y, x+width, y+height],
                        fill='#FFEBEE', outline='#FF0000', width=2)
            draw.text((x + width//2, y + height//2), 
                    "Error creating card",
                    fill='#FF0000', 
                    font=self.text_font,
                    anchor="mm")

    def generate_image(self, grad_year, leaderboard_data, start_date=None, end_date=None):
        """Generate the complete social media image"""
        width, height = 1080, 1080
        img, draw = self.create_background(width, height)
        
        # Header section
        title_y = 40
        # Draw title shadow
        shadow_offset = 2
        title_text = f"Class of {grad_year}"
        draw.text((width//2+shadow_offset, title_y+shadow_offset), title_text,
                 fill='#00000022', font=self.title_font, anchor="mt")
        # Draw title
        draw.text((width//2, title_y), title_text,
                 fill=self.COLORS['primary'], font=self.title_font, anchor="mt")
        
        # Subtitle
        subtitle_y = title_y + 80
        draw.text((width//2, subtitle_y), "Baseball Performance Leaderboards",
                 fill=self.COLORS['secondary'], font=self.header_font, anchor="mt")
        
        # Date range
        if start_date and end_date:
            date_text = f"Data from {start_date} to {end_date}"
        else:
            date_text = f"Data as of {datetime.now().strftime('%B %d, %Y')}"
        date_y = subtitle_y + 50
        draw.text((width-40, date_y), date_text,
                 fill=self.COLORS['text_dark'], font=self.text_font, anchor="rt")

        # Layout calculation
        content_start_y = date_y + 60
        content_height = height - content_start_y - 40
        section_height = content_height // 2
        
        # Sections
        sections = [
            ('Max Exit Velocity', 'max-exit-velocity'),
            ('Average Exit Velocity', 'average-exit-velocity'),
            ('Max Distance', 'max-distance'),
            ('Average Distance', 'average-distance')
        ]
        
        # Draw sections in a tighter grid
        for idx, (title, metric_key) in enumerate(sections):
            col = idx % 2
            row = idx // 2
            
            section_x = col * (width // 2) + 30
            section_y = content_start_y + (row * section_height)
            
            # Section title
            draw.text((section_x, section_y), title,
                     fill=self.COLORS['primary'], font=self.subheader_font)
            
            # Player cards
            metric_data = leaderboard_data.get(metric_key, {}).get(grad_year, [])
            card_start_y = section_y + 40
            
            for i, player in enumerate(metric_data[:5]):
                self.create_player_card(
                    draw, 
                    section_x, 
                    card_start_y + (i * (120 + 10)),  # Card height + spacing
                    player,
                    width=480  # Adjusted card width
                )
        
        # Save high-quality image
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', quality=95, optimize=True)
        img_buffer.seek(0)
        return img_buffer