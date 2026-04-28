#!/usr/bin/env python3
"""
Annotate key figures with highlights, circles, arrows, and text annotations.
This script adds visual emphasis to critical findings for better exam presentation.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

# Configuration
FIGURES_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'

# Define annotations for each figure
ANNOTATIONS = {
    # CATEGORY 01: Product & Market Dominance
    '01_product_market_dominance/category_pie.png': {
        'name': 'Streetwear Monopoly',
        'annotations': [
            {
                'type': 'highlight_sector',
                'position': (80, 20),  # Top right area
                'text': '80% STREETWEAR\n486K units',
                'color': '#CE2626',
                'radius': 120
            }
        ]
    },
    
    '01_product_market_dominance/segment_market_share_new.png': {
        'name': 'Market Share Concentration',
        'annotations': [
            {
                'type': 'arrow_and_text',
                'from': (150, 50),
                'to': (200, 150),
                'text': 'Declining\nGrowth',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/margin_by_size.png': {
        'name': 'Size-Based Margin Gap',
        'annotations': [
            {
                'type': 'highlight_box',
                'coords': (70, 20, 95, 100),  # L/XL region (estimated)
                'text': 'Premium\nMargin',
                'color': '#2D5016'
            },
            {
                'type': 'highlight_box',
                'coords': (20, 60, 45, 100),  # S/M region
                'text': 'Commodity\nMargin',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_new.png': {
        'name': 'Profitability by Size',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (85, 30),
                'text': 'Gap: 12-17pp',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_boxplot.png': {
        'name': 'Size Distribution Variance',
        'annotations': [
            {
                'type': 'bracket',
                'start': (70, 10),
                'end': (95, 10),
                'text': '12-17pp Margin Gap',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/monthly_trend_heatmap.png': {
        'name': 'May Peak Seasonality',
        'annotations': [
            {
                'type': 'highlight_cell',
                'coords': (75, 15, 90, 35),  # May area
                'text': 'May: 2.6x Peak',
                'color': '#2D5016'
            }
        ]
    },
    
    '01_product_market_dominance/star_vs_bait_analysis.png': {
        'name': 'Star vs Bait Classification',
        'annotations': [
            {
                'type': 'label_region',
                'coords': (80, 20),
                'text': 'STAR\n31.3% Margin',
                'color': '#2D5016'
            },
            {
                'type': 'label_region',
                'coords': (20, 80),
                'text': 'BAIT\n23-24% Margin',
                'color': '#CE2626'
            }
        ]
    },
    
    # CATEGORY 02: Customer Lifecycle
    '02_customer_lifecycle_acquisition/cohort_growth.png': {
        'name': 'Cohort Retention Collapse',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (20, 40),
                'text': '40%→10%\nRetention\nCollapse',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/repeat_rate_by_channel.png': {
        'name': 'Channel LTV Disparity',
        'annotations': [
            {
                'type': 'highlight_bar',
                'position': (20, 50),
                'text': 'Organic: 38%',
                'color': '#2D5016',
                'width': 25
            },
            {
                'type': 'highlight_bar',
                'position': (70, 50),
                'text': 'Double-Day: 8%',
                'color': '#CE2626',
                'width': 8
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_by_channel.png': {
        'name': 'LTV by Acquisition Channel',
        'annotations': [
            {
                'type': 'bracket',
                'start': (20, 5),
                'end': (40, 5),
                'text': 'High LTV',
                'color': '#2D5016'
            },
            {
                'type': 'bracket',
                'start': (70, 5),
                'end': (85, 5),
                'text': 'Low LTV (Loss)',
                'color': '#CE2626'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_demographics_heatmap.png': {
        'name': 'LTV by Demographics',
        'annotations': [
            {
                'type': 'highlight_region',
                'coords': (70, 20, 95, 50),  # Premium customers
                'text': 'High-Value\nSegment',
                'color': '#2D5016'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/acquisition_efficiency.png': {
        'name': 'Acquisition Efficiency Trends',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (50, 30),
                'text': 'CAC Rising\nLTV Falling',
                'color': '#CE2626',
                'direction': 'up'
            }
        ]
    },
    
    # CATEGORY 03: Operational Friction
    '03_operational_friction_leakage/returns_bar.png': {
        'name': 'Returns by Reason',
        'annotations': [
            {
                'type': 'highlight_bar',
                'position': (35, 50),
                'text': 'Wrong Size\n34.6%',
                'color': '#CE2626',
                'width': 35
            }
        ]
    },
    
    '03_operational_friction_leakage/return_deep_dive.png': {
        'name': 'Wrong-Size Return Deep Dive',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (40, 20),
                'text': '3.5pp Margin\nErosion',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_friction_matrix.png': {
        'name': 'Return Friction by Size',
        'annotations': [
            {
                'type': 'highlight_region',
                'coords': (15, 15, 35, 35),  # S/M region
                'text': 'High Return\nRate',
                'color': '#CE2626'
            },
            {
                'type': 'highlight_region',
                'coords': (75, 75, 95, 95),  # L/XL region
                'text': 'Low Return',
                'color': '#2D5016'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_reason_matrix.png': {
        'name': 'Return Reason Heatmap',
        'annotations': [
            {
                'type': 'circle_annotation',
                'center': (35, 25),
                'radius': 30,
                'text': 'Wrong Size\nHotspot',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/tet_holiday_friction.png': {
        'name': 'Tết Holiday Delivery Friction',
        'annotations': [
            {
                'type': 'highlight_region',
                'coords': (15, 20, 40, 50),  # Post-Tết period
                'text': 'Post-Tết\n8.2% Failure',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/seasonal_operational_patterns.png': {
        'name': 'Operational Patterns by Season',
        'annotations': [
            {
                'type': 'label_region',
                'coords': (45, 20),
                'text': 'Post-Tết\nSurge',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/inventory_risk_analysis.png': {
        'name': 'Inventory Risk Heatmap',
        'annotations': [
            {
                'type': 'highlight_region',
                'coords': (20, 60, 50, 100),  # Overstock risk
                'text': 'Overstock\nRisk',
                'color': '#CE2626'
            },
            {
                'type': 'highlight_region',
                'coords': (70, 20, 95, 40),  # Stockout risk
                'text': 'Stockout',
                'color': '#2D5016'
            }
        ]
    },
    
    '03_operational_friction_leakage/shipping_delivery_efficiency.png': {
        'name': 'Shipping Delivery Efficiency',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (75, 30),
                'text': 'Peak Lag',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
    
    # CATEGORY 04: Financial Dynamics
    '04_financial_payment_dynamics/payment_analysis.png': {
        'name': 'Payment Method Distribution',
        'annotations': [
            {
                'type': 'highlight_sector',
                'position': (70, 30),
                'text': 'Installment:\n22% Orders\n28% Revenue',
                'color': '#2D5016',
                'radius': 80
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_aov_boxplot.png': {
        'name': 'Installment AOV Lift',
        'annotations': [
            {
                'type': 'bracket',
                'start': (20, 5),
                'end': (80, 5),
                'text': '+35% AOV Lift',
                'color': '#2D5016'
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_revenue_share.png': {
        'name': 'Installment Revenue Contribution',
        'annotations': [
            {
                'type': 'highlight_bar',
                'position': (50, 50),
                'text': '28% Revenue\nfrom\n22% Orders',
                'color': '#2D5016',
                'width': 28
            }
        ]
    },
    
    '04_financial_payment_dynamics/monthly_installments_trend.png': {
        'name': 'Installment Adoption Trend',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (80, 30),
                'text': 'Growth\nOpportunity\n(Current 22%)',
                'color': '#2D5016',
                'direction': 'up'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promotion_impact.png': {
        'name': 'Promotion Impact on Volume',
        'annotations': [
            {
                'type': 'highlight_region',
                'coords': (40, 30, 65, 70),  # Optimal range
                'text': 'Optimal Zone\n15-25%',
                'color': '#2D5016'
            },
            {
                'type': 'highlight_region',
                'coords': (70, 20, 100, 50),  # Diminishing returns
                'text': 'Diminishing\nReturns',
                'color': '#CE2626'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_depth_volume.png': {
        'name': 'Promotion Depth vs Volume',
        'annotations': [
            {
                'type': 'circle_annotation',
                'center': (50, 50),
                'radius': 40,
                'text': 'Optimal\nPoint',
                'color': '#2D5016'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_urgency_stackability.png': {
        'name': 'Promotion Urgency & Stackability',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (60, 20),
                'text': 'Race to\nBottom',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
    
    '04_financial_payment_dynamics/revenue_margin_trend.png': {
        'name': 'Revenue vs Margin Trend',
        'annotations': [
            {
                'type': 'arrow_annotation',
                'position': (80, 50),
                'text': 'Revenue UP\nMargin DOWN',
                'color': '#CE2626',
                'direction': 'down'
            }
        ]
    },
}


def add_text_annotation(draw, position, text, color='#CE2626', bg_color='white', font_size=12):
    """Add text annotation with background"""
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Add padding
    padding = 5
    bg_box = (
        position[0] - padding,
        position[1] - padding,
        position[0] + text_width + padding,
        position[1] + text_height + padding
    )
    
    # Draw background
    draw.rectangle(bg_box, fill=bg_color, outline=color, width=2)
    
    # Draw text
    draw.text((position[0], position[1]), text, fill=color, font=font)


def add_circle_highlight(draw, center, radius, color='#CE2626', width=3):
    """Add circle highlight"""
    x, y = center
    bbox = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(bbox, outline=color, width=width)


def add_arrow(draw, start, end, color='#CE2626', width=3):
    """Add arrow annotation"""
    # Draw line
    draw.line([start, end], fill=color, width=width)
    
    # Draw arrowhead
    import math
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    arrow_size = 15
    
    p1 = (
        end[0] - arrow_size * math.cos(angle - math.pi / 6),
        end[1] - arrow_size * math.sin(angle - math.pi / 6)
    )
    p2 = (
        end[0] - arrow_size * math.cos(angle + math.pi / 6),
        end[1] - arrow_size * math.sin(angle + math.pi / 6)
    )
    
    draw.polygon([end, p1, p2], fill=color)


def add_bracket(draw, start, end, text, color='#CE2626', font_size=10):
    """Add bracket annotation"""
    # Draw horizontal lines at ends
    bracket_height = 10
    draw.line([(start[0], start[1]), (start[0], start[1] - bracket_height)], fill=color, width=2)
    draw.line([(end[0], end[1]), (end[0], end[1] - bracket_height)], fill=color, width=2)
    
    # Draw connecting line
    draw.line([(start[0], start[1] - bracket_height), (end[0], end[1] - bracket_height)], fill=color, width=2)
    
    # Add text in middle
    mid_x = (start[0] + end[0]) // 2
    text_y = start[1] - bracket_height - 15
    add_text_annotation(draw, (mid_x - 30, text_y), text, color, font_size=font_size)


def annotate_figure(image_path, annotations):
    """Add annotations to a single figure"""
    try:
        # Load image
        img = Image.open(image_path)
        width, height = img.size
        
        # Create copy for annotation
        img_annotated = img.copy()
        draw = ImageDraw.Draw(img_annotated, 'RGBA')
        
        # Add annotations
        for annotation in annotations:
            ann_type = annotation.get('type')
            color = annotation.get('color', '#CE2626')
            
            # Convert percentage coordinates to pixel coordinates
            def pct_to_px(pct_pos):
                if isinstance(pct_pos, tuple):
                    return (int(width * pct_pos[0] / 100), int(height * pct_pos[1] / 100))
                return int(width * pct_pos / 100)
            
            if ann_type == 'highlight_sector':
                pos = pct_to_px(annotation['position'])
                radius = annotation.get('radius', 50)
                text = annotation.get('text', '')
                add_circle_highlight(draw, pos, radius, color, width=3)
                add_text_annotation(draw, (pos[0] - 40, pos[1] - 20), text, color, font_size=11)
            
            elif ann_type == 'highlight_box':
                coords = annotation['coords']
                px_coords = (pct_to_px((coords[0], coords[1])), pct_to_px((coords[2], coords[3])))
                x1, y1 = px_coords[0]
                x2, y2 = px_coords[1]
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                text = annotation.get('text', '')
                add_text_annotation(draw, (x1 + 5, y1 + 5), text, color, font_size=10)
            
            elif ann_type == 'arrow_annotation':
                pos = pct_to_px(annotation['position'])
                text = annotation.get('text', '')
                direction = annotation.get('direction', 'down')
                
                if direction == 'down':
                    end = (pos[0], pos[1] + 40)
                else:
                    end = (pos[0], pos[1] - 40)
                
                add_arrow(draw, pos, end, color)
                add_text_annotation(draw, (pos[0] - 30, pos[1] + 50 if direction == 'down' else pos[1] - 70), 
                                  text, color, font_size=10)
            
            elif ann_type == 'arrow_and_text':
                start = pct_to_px(annotation['from'])
                end = pct_to_px(annotation['to'])
                text = annotation.get('text', '')
                add_arrow(draw, start, end, color)
                add_text_annotation(draw, (end[0] + 10, end[1]), text, color, font_size=10)
            
            elif ann_type == 'bracket':
                start = pct_to_px(annotation['start'])
                end = pct_to_px(annotation['end'])
                text = annotation.get('text', '')
                add_bracket(draw, start, end, text, color, font_size=10)
            
            elif ann_type == 'highlight_bar':
                pos = pct_to_px(annotation['position'])
                bar_width = pct_to_px(annotation.get('width', 25))
                text = annotation.get('text', '')
                draw.rectangle([pos[0], pos[1], pos[0] + bar_width, pos[1] + 40], 
                             outline=color, width=3)
                add_text_annotation(draw, (pos[0] + 5, pos[1] + 5), text, color, font_size=9)
            
            elif ann_type == 'circle_annotation':
                center = pct_to_px(annotation['center'])
                radius = annotation.get('radius', 40)
                text = annotation.get('text', '')
                add_circle_highlight(draw, center, radius, color, width=3)
                add_text_annotation(draw, (center[0] - 30, center[1] - 20), text, color, font_size=10)
            
            elif ann_type == 'highlight_region':
                coords = annotation['coords']
                x1, y1, x2, y2 = coords
                px1 = pct_to_px((x1, y1))
                px2 = pct_to_px((x2, y2))
                draw.rectangle([px1[0], px1[1], px2[0], px2[1]], outline=color, width=3)
                text = annotation.get('text', '')
                add_text_annotation(draw, (px1[0] + 5, px1[1] + 5), text, color, font_size=10)
            
            elif ann_type == 'label_region':
                coords = annotation['coords']
                pos = pct_to_px(coords)
                text = annotation.get('text', '')
                add_text_annotation(draw, pos, text, color, font_size=11)
            
            elif ann_type == 'highlight_cell':
                coords = annotation['coords']
                x1, y1, x2, y2 = coords
                px1 = pct_to_px((x1, y1))
                px2 = pct_to_px((x2, y2))
                draw.rectangle([px1[0], px1[1], px2[0], px2[1]], outline=color, width=3)
                text = annotation.get('text', '')
                add_text_annotation(draw, (px1[0] - 60, px1[1] - 30), text, color, font_size=10)
        
        # Save annotated image
        img_annotated.save(image_path)
        return True
    except Exception as e:
        print(f"  ❌ Error annotating {image_path}: {e}")
        return False


def main():
    """Main annotation pipeline"""
    print("=" * 70)
    print("🎨 FIGURE ANNOTATION PIPELINE")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for rel_path, config in ANNOTATIONS.items():
        full_path = os.path.join(FIGURES_DIR, rel_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  SKIP: {rel_path} (file not found)")
            fail_count += 1
            continue
        
        print(f"\n✏️  Annotating: {config['name']}")
        print(f"   File: {rel_path}")
        
        if annotate_figure(full_path, config['annotations']):
            print(f"   ✅ Success ({len(config['annotations'])} annotations added)")
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Annotation Complete: {success_count} figures annotated")
    if fail_count > 0:
        print(f"⚠️  {fail_count} figures skipped")
    print("=" * 70)
    
    return success_count, fail_count


if __name__ == '__main__':
    main()
