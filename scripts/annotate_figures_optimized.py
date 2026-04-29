#!/usr/bin/env python3
"""
ADVANCED FIGURE ANNOTATION WITH DYNAMIC SIZING
- Adaptive font sizes based on image dimensions
- Proportional text boxes, circles, brackets, arrows
- Smart text hierarchy (critical/secondary/tertiary)
- Professional typography with proper spacing
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = '/home/shayneeo/Downloads/Datathon'
FIGURES_DIR = os.path.join(REPO_ROOT, 'output', 'figures_living')

# INTELLIGENT ANNOTATIONS WITH DYNAMIC SIZING
ADVANCED_ANNOTATIONS = {
    # ============================================================================
    # CATEGORY 01: Product & Market Dominance
    # ============================================================================
    
    '01_product_market_dominance/category_pie.png': {
        'name': 'Streetwear Monopoly (Pie)',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'pie_slice_critical',
                'angle_range': (0, 290),
                'text': '80% STREETWEAR\n486K units',
                'color': '#CE2626',
                'text_level': 'primary',
                'radius_pct': 54
            }
        ]
    },
    
    '01_product_market_dominance/segment_market_share_new.png': {
        'name': 'Market Share Trend',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'trend_decline_arrow',
                'start_pct': (75, 30),
                'end_pct': (90, 55),
                'text': 'Declining\nGrowth',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    '01_product_market_dominance/margin_by_size.png': {
        'name': 'Size Profitability Gap',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'bar_group_premium',
                'left_pct': 75,
                'right_pct': 95,
                'y_middle_pct': 35,
                'text': 'Premium\n30–35%',
                'color': '#2D5016',
                'text_level': 'primary'
            },
            {
                'type': 'bar_group_commodity',
                'left_pct': 20,
                'right_pct': 40,
                'y_middle_pct': 60,
                'text': 'Commodity\n18–26%',
                'color': '#CE2626',
                'text_level': 'primary'
            },
            {
                'type': 'gap_bracket_central',
                'left_pct': 10,
                'right_pct': 10,
                'top_pct': 15,
                'text': '12-17pp\nMargin\nGap',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_new.png': {
        'name': 'Profitability Gap',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'vertical_gap',
                'left_pct': 75,
                'right_pct': 90,
                'top_pct': 25,
                'bottom_pct': 70,
                'text': 'Gap:\n12-17pp',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_boxplot.png': {
        'name': 'Size Distribution Advantage',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'boxplot_span_bracket',
                'left_pct': 20,
                'right_pct': 80,
                'bracket_y_pct': 10,
                'text': 'Premium Size\n12–17pp',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '01_product_market_dominance/monthly_trend_heatmap.png': {
        'name': 'May Peak Seasonality',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'heatmap_cell_peak',
                'col_pct': 42,
                'text': 'May Peak\n2.6x',
                'color': '#2D5016',
                'text_level': 'primary'
            }
        ]
    },
    
    '01_product_market_dominance/star_vs_bait_analysis.png': {
        'name': 'Star vs Bait Portfolio',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'quadrant_star',
                'position': (80, 25),
                'text': 'STAR\n31.3%\nMargin',
                'color': '#2D5016',
                'text_level': 'primary'
            },
            {
                'type': 'quadrant_bait',
                'position': (20, 75),
                'text': 'BAIT\n23-24%\nMargin',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '01_product_market_dominance/brand_performance.png': {
        'name': 'Brand Performance',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'warning_label',
                'position_pct': (72, 18),
                'text': 'UR = STAR\nPremium lead',
                'color': '#2D5016',
                'text_level': 'secondary'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 02: Customer Lifecycle & Acquisition
    # ============================================================================
    
    '02_customer_lifecycle_acquisition/cohort_growth.png': {
        'name': 'Retention Collapse',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'line_collapse_arrow',
                'start_pct': (15, 25),
                'end_pct': (85, 80),
                'text': 'Retention\n40→10%',
                'color': '#CE2626',
                'text_level': 'primary',
                'curve': True
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/repeat_rate_by_channel.png': {
        'name': 'Channel Repeat Disparity',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'bar_organic_highlight',
                'position_pct': (25, 50),
                'height_pct': 28,
                'text': 'Organic\n38%',
                'color': '#2D5016',
                'text_level': 'primary'
            },
            {
                'type': 'bar_double_day_highlight',
                'position_pct': (70, 70),
                'height_pct': 10,
                'text': 'Double-Day\n8%',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_by_channel.png': {
        'name': 'LTV by Channel',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'bar_span_high_ltv',
                'left_pct': 15,
                'right_pct': 40,
                'bracket_y_pct': 5,
                'text': 'High LTV',
                'color': '#2D5016',
                'text_level': 'secondary'
            },
            {
                'type': 'bar_span_low_ltv',
                'left_pct': 65,
                'right_pct': 85,
                'bracket_y_pct': 5,
                'text': 'Low LTV',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_demographics_heatmap.png': {
        'name': 'High-Value Segment',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'heatmap_premium_segment',
                'center_pct': (80, 30),
                'text': 'Premium\nSegment',
                'color': '#2D5016',
                'text_level': 'primary'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/acquisition_efficiency.png': {
        'name': 'CAC/LTV Crisis',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'diverging_lines',
                'position_pct': (70, 50),
                'text': 'CAC ↑\nLTV ↓',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/line_revenue_acquisition.png': {
        'name': 'Line Revenue Acquisition',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'warning_label',
                'position_pct': (72, 18),
                'text': 'Organic >\nDouble-Day',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 03: Operational Friction & Leakage
    # ============================================================================
    
    '03_operational_friction_leakage/returns_bar.png': {
        'name': 'Wrong-Size Returns Crisis',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'bar_critical_highlight',
                'position_pct': (35, 50),
                'text': 'Wrong Size\n34.6%\n-3.5pp',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_deep_dive.png': {
        'name': 'Margin Impact',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'impact_arrow_down',
                'position_pct': (50, 40),
                'text': 'Margin\n-3.5pp',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_friction_matrix.png': {
        'name': 'Size Return Contrast',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'heatmap_dual_contrast',
                'problem_pct': (25, 25),
                'solution_pct': (75, 75),
                'problem_text': 'High\nReturn\n(S/M)',
                'solution_text': 'Low\nReturn\n(L/XL)',
                'problem_color': '#CE2626',
                'solution_color': '#2D5016',
                'text_level': 'secondary'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_reason_matrix.png': {
        'name': 'Wrong-Size Hotspot',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'heatmap_critical_hotspot',
                'center_pct': (35, 25),
                'text': 'Wrong-Size',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '03_operational_friction_leakage/tet_holiday_friction.png': {
        'name': 'Post-Tết Failure Spike',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'time_period_region',
                'left_pct': 15,
                'right_pct': 40,
                'text': 'Tết\n8.2% Fail',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '03_operational_friction_leakage/seasonal_operational_patterns.png': {
        'name': 'Post-Tét Surge',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'seasonal_label',
                'position_pct': (40, 30),
                'text': 'Post-Tét\nSurge',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    '03_operational_friction_leakage/line_failure_rate.png': {
        'name': 'Line Failure Rate',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'warning_label',
                'position_pct': (72, 18),
                'text': 'UC / RP\nhotspot',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    '03_operational_friction_leakage/inventory_risk_analysis.png': {
        'name': 'Inventory Misalignment',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'heatmap_dual_risk',
                'overstock_pct': (25, 65),
                'stockout_pct': (75, 25),
                'overstock_text': 'Overstock',
                'stockout_text': 'Stockout',
                'problem_color': '#CE2626',
                'solution_color': '#2D5016',
                'text_level': 'primary'
            }
        ]
    },
    
    '03_operational_friction_leakage/shipping_delivery_efficiency.png': {
        'name': 'Peak Delivery Lag',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'lag_arrow_down',
                'position_pct': (70, 35),
                'text': 'Peak\nLag',
                'color': '#CE2626',
                'text_level': 'secondary'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 04: Financial Dynamics & Payment
    # ============================================================================
    
    '04_financial_payment_dynamics/payment_analysis.png': {
        'name': 'Installment Opportunity',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'pie_slice_opportunity',
                'angle_start': 80,
                'angle_end': 240,
                'text': 'Installment\n22%→28%',
                'color': '#2D5016',
                'text_level': 'primary',
                'radius_pct': 52
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_aov_boxplot.png': {
        'name': 'AOV Lift Impact',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'box_span_lift',
                'left_pct': 25,
                'right_pct': 75,
                'bracket_y_pct': 10,
                'text': '+35% AOV',
                'color': '#2D5016',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_revenue_share.png': {
        'name': 'Revenue Premium',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'bar_revenue_premium',
                'left_position_pct': (25, 50),
                'right_position_pct': (75, 65),
                'left_text': '22%\nOrders',
                'right_text': '28%\nRevenue',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/monthly_installments_trend.png': {
        'name': 'Growth Potential',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'growth_arrow_up',
                'position_pct': (75, 35),
                'text': 'Growth\nOpport.',
                'color': '#2D5016',
                'text_level': 'secondary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promotion_impact.png': {
        'name': 'Optimal Discount Zone',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'curve_dual_zone',
                'optimal_left_pct': 40,
                'optimal_right_pct': 65,
                'diminishing_left_pct': 65,
                'diminishing_right_pct': 100,
                'optimal_text': 'Optimal\n15–25%',
                'diminishing_text': 'Diminishing',
                'optimal_color': '#2D5016',
                'diminishing_color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_depth_volume.png': {
        'name': 'Elasticity Peak',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'scatter_optimal_point',
                'center_pct': (50, 50),
                'text': 'Optimal',
                'color': '#2D5016',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_urgency_stackability.png': {
        'name': 'Competitive Race',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'warning_label',
                'position_pct': (50, 50),
                'text': 'Race to\nBottom',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/revenue_margin_trend.png': {
        'name': 'Growth Paradox',
        'critical_finding': True,
        'annotations': [
            {
                'type': 'diverging_trend',
                'position_pct': (80, 50),
                'text': 'Revenue ↑\nMargin ↓',
                'color': '#CE2626',
                'text_level': 'primary'
            }
        ]
    },
    
    '04_financial_payment_dynamics/line_financial_impact.png': {
        'name': 'Line Financial Impact',
        'critical_finding': False,
        'annotations': [
            {
                'type': 'warning_label',
                'position_pct': (72, 18),
                'text': 'UR\nmargin lead',
                'color': '#2D5016',
                'text_level': 'secondary'
            }
        ]
    },
}


def annotate_relpath(rel_path):
    config = ADVANCED_ANNOTATIONS.get(rel_path)
    if not config:
        return False
    full_path = os.path.join(FIGURES_DIR, rel_path)
    if not os.path.exists(full_path):
        return False
    return annotate_figure(full_path, config['annotations'])


def annotate_relpaths(rel_paths):
    results = []
    for rel_path in rel_paths:
        results.append(annotate_relpath(rel_path))
    return results


def get_dynamic_sizing(width, height):
    """Calculate font sizes and element dimensions based on image size"""
    diagonal = math.sqrt(width**2 + height**2)

    sizing = {
        # Keep text readable after downscaling in markdown/PDF while preventing oversize overlays.
        'primary_font': min(36, max(12, int(diagonal / 170 + 2))),  # Critical findings
        'secondary_font': min(30, max(10, int(diagonal / 180))),     # Context
        'tertiary_font': min(24, max(8, int(diagonal / 200 - 1))),   # Supporting
        'text_padding': max(5, int(width * 0.008)),                  # Text box padding
        'arrow_width': max(2, int(diagonal / 260)),                  # Arrow thickness
        'circle_radius': min(100, max(24, int(diagonal * 0.018))),   # Circle size
        'bracket_height': min(80, max(14, int(diagonal * 0.02))),    # Bracket height
        'border_width': 2,                                           # Fixed border
    }
    
    return sizing


def get_font(font_size):
    """Load font with given size"""
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        return ImageFont.load_default()


def add_smart_text_box(draw, position, text, font_size, color='#CE2626', padding=8):
    """Add text with a clamped, readable text box and return useful anchor points."""
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    canvas_w, canvas_h = draw._image.size
    margin = max(8, padding)
    x = min(max(position[0], margin), canvas_w - text_width - padding - margin)
    y = min(max(position[1], margin), canvas_h - text_height - padding - margin)

    # Text box with padding
    bg_box = (
        x - padding,
        y - padding,
        x + text_width + padding,
        y + text_height + padding
    )

    # Draw background
    draw.rectangle(bg_box, fill=(255, 255, 255, 235), outline=color, width=max(2, font_size // 10))

    # Draw text
    draw.text((x, y), text, fill=color, font=font)

    return {
        'box': bg_box,
        'anchors': {
            'left': (bg_box[0], (bg_box[1] + bg_box[3]) // 2),
            'right': (bg_box[2], (bg_box[1] + bg_box[3]) // 2),
            'top': ((bg_box[0] + bg_box[2]) // 2, bg_box[1]),
            'bottom': ((bg_box[0] + bg_box[2]) // 2, bg_box[3]),
            'center': ((bg_box[0] + bg_box[2]) // 2, (bg_box[1] + bg_box[3]) // 2),
        }
    }


def add_arrow_with_head(draw, start, end, color='#CE2626', width=3):
    """Draw arrow with arrowhead"""
    draw.line([start, end], fill=color, width=width)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    arrow_size = max(10, int(width * 2.5))
    
    p1 = (
        end[0] - arrow_size * math.cos(angle - math.pi / 6),
        end[1] - arrow_size * math.sin(angle - math.pi / 6)
    )
    p2 = (
        end[0] - arrow_size * math.cos(angle + math.pi / 6),
        end[1] - arrow_size * math.sin(angle + math.pi / 6)
    )
    
    draw.polygon([end, p1, p2], fill=color)


def add_circle_outline(draw, center, radius, color='#CE2626', width=3):
    """Draw circle outline"""
    x, y = center
    bbox = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(bbox, outline=color, width=width)


def annotate_figure(image_path, annotations):
    """Annotate figure with dynamic sizing"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        sizing = get_dynamic_sizing(width, height)
        
        img_annotated = img.copy()
        draw = ImageDraw.Draw(img_annotated, 'RGBA')
        
        def pct_to_px(pct_val):
            if isinstance(pct_val, tuple):
                return (int(width * pct_val[0] / 100), int(height * pct_val[1] / 100))
            return int(width * pct_val / 100) if pct_val <= 100 else int(pct_val)
        
        for ann in annotations:
            ann_type = ann.get('type')
            color = ann.get('color', '#CE2626')
            text_level = ann.get('text_level', 'secondary')
            font_size = sizing[f'{text_level}_font']
            
            # PIE ANNOTATIONS
            if ann_type == 'pie_slice_critical':
                center = (width // 2, height // 2)
                radius = min(width, height) * ann.get('radius_pct', 65) / 200
                add_circle_outline(draw, center, int(radius), color, sizing['border_width'] + 1)

                text = ann.get('text', '')
                right_x = int(center[0] + radius + width * 0.04)
                left_x = int(center[0] - radius - width * 0.18)
                on_right_side = right_x < int(width * 0.78)
                text_pos = (right_x, int(center[1] - height * 0.08)) if on_right_side else (left_x, int(center[1] - height * 0.08))
                text_box = add_smart_text_box(draw, text_pos, text, font_size, color, sizing['text_padding'])
                target = (
                    int(center[0] + radius * 0.72),
                    int(center[1] - radius * 0.10)
                ) if on_right_side else (
                    int(center[0] - radius * 0.72),
                    int(center[1] - radius * 0.10)
                )
                arrow_start = text_box['anchors']['left'] if on_right_side else text_box['anchors']['right']
                add_arrow_with_head(draw, arrow_start, target, color, sizing['arrow_width'])
            
            elif ann_type == 'pie_slice_opportunity':
                center = (width // 2, height // 2)
                radius = min(width, height) * ann.get('radius_pct', 60) / 200
                add_circle_outline(draw, center, int(radius * 0.9), color, sizing['border_width'] + 1)

                text = ann.get('text', '')
                right_x = int(center[0] + radius + width * 0.03)
                left_x = int(center[0] - radius - width * 0.20)
                on_right_side = right_x < int(width * 0.80)
                text_pos = (right_x, int(center[1] - height * 0.10)) if on_right_side else (left_x, int(center[1] - height * 0.10))
                text_box = add_smart_text_box(draw, text_pos, text, font_size, color, sizing['text_padding'])
                target = (
                    int(center[0] + radius * 0.68),
                    int(center[1] - radius * 0.18)
                ) if on_right_side else (
                    int(center[0] - radius * 0.68),
                    int(center[1] - radius * 0.18)
                )
                arrow_start = text_box['anchors']['left'] if on_right_side else text_box['anchors']['right']
                add_arrow_with_head(draw, arrow_start, target, color, sizing['arrow_width'])
            
            # BAR ANNOTATIONS
            elif ann_type in ['bar_group_premium', 'bar_group_commodity']:
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                y_mid = pct_to_px(ann['y_middle_pct'])
                box_half_h = min(max(28, int(height * 0.045)), 90)

                # Box around bars
                draw.rectangle([left, y_mid - box_half_h, right, y_mid + box_half_h], outline=color, width=sizing['border_width'] + 1)

                text = ann.get('text', '')
                text_x = (left + right) // 2 - 50
                add_smart_text_box(draw, (text_x, y_mid - box_half_h - int(height * 0.03)), text, font_size, color, sizing['text_padding'])
            
            elif ann_type in ['bar_critical_highlight', 'bar_organic_highlight', 'bar_double_day_highlight']:
                pos = pct_to_px(ann['position_pct'])
                height_px = min(pct_to_px(ann.get('height_pct', 30)), int(height * 0.24))
                bar_half_w = min(max(22, int(width * 0.016)), 80)

                draw.rectangle([pos[0] - bar_half_w, pos[1] - height_px, pos[0] + bar_half_w, pos[1]],
                             outline=color, width=sizing['border_width'])

                text = ann.get('text', '')
                add_smart_text_box(draw, (pos[0] - bar_half_w, pos[1] - height_px - int(height * 0.025)), text, font_size, color, sizing['text_padding'])
            
            elif ann_type in ['bar_span_high_ltv', 'bar_span_low_ltv', 'box_span_lift']:
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                bracket_y = pct_to_px(ann['bracket_y_pct'])

                bracket_h = min(sizing['bracket_height'], 70)
                draw.line([(left, bracket_y), (left, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(right, bracket_y), (right, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(left, bracket_y - bracket_h), (right, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                
                text = ann.get('text', '')
                text_x = (left + right) // 2 - 70
                add_smart_text_box(draw, (text_x, bracket_y - bracket_h - 60), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'gap_bracket_central':
                bracket_h = min(sizing['bracket_height'] * 2, 80)
                top = pct_to_px(ann['top_pct'])
                left_pos = int(width * 0.45)
                right_pos = int(width * 0.55)
                
                draw.line([(left_pos, top), (left_pos, top - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(right_pos, top), (right_pos, top - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(left_pos, top - bracket_h), (right_pos, top - bracket_h)], fill=color, width=sizing['border_width'])
                
                text = ann.get('text', '')
                add_smart_text_box(draw, ((left_pos + right_pos) // 2 - 50, top - bracket_h - 80), text, font_size, color, sizing['text_padding'])
            
            # LINE ANNOTATIONS
            elif ann_type == 'trend_decline_arrow':
                start = pct_to_px(ann['start_pct'])
                end = pct_to_px(ann['end_pct'])
                add_arrow_with_head(draw, start, end, color, sizing['arrow_width'] + 1)
                
                text = ann.get('text', '')
                text_offset = ann.get('text_offset', (15, 10))
                add_smart_text_box(draw, (end[0] + text_offset[0], end[1] + text_offset[1]), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'line_collapse_arrow':
                start = pct_to_px(ann['start_pct'])
                end = pct_to_px(ann['end_pct'])
                add_arrow_with_head(draw, start, end, color, sizing['arrow_width'] + 2)
                
                text = ann.get('text', '')
                mid_x = (start[0] + end[0]) // 2
                mid_y = (start[1] + end[1]) // 2
                add_smart_text_box(draw, (mid_x - 60, mid_y - 100), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'diverging_lines':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text_box(draw, (pos[0] - 50, pos[1] - 50), text, font_size, color, sizing['text_padding'])
            
            # HEATMAP ANNOTATIONS
            elif ann_type == 'heatmap_cell_peak':
                col_x = pct_to_px(ann['col_pct'])
                cell_center = (col_x, height // 2)
                add_circle_outline(draw, cell_center, min(sizing['circle_radius'], 72), color, sizing['border_width'])

                text = ann.get('text', '')
                add_smart_text_box(draw, (col_x - 44, height - 150), text, font_size, color, sizing['text_padding'])
            
            elif ann_type in ['heatmap_premium_segment', 'heatmap_critical_hotspot']:
                center = pct_to_px(ann['center_pct'])
                add_circle_outline(draw, center, min(sizing['circle_radius'], 84), color, sizing['border_width'])

                text = ann.get('text', '')
                add_smart_text_box(draw, (center[0] - 44, center[1] - 96), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'heatmap_dual_contrast':
                problem = pct_to_px(ann['problem_pct'])
                solution = pct_to_px(ann['solution_pct'])

                add_circle_outline(draw, problem, min(sizing['circle_radius'], 78), ann['problem_color'], sizing['border_width'])
                add_smart_text_box(draw, (problem[0] - 52, problem[1] - 86), ann['problem_text'], font_size, ann['problem_color'], sizing['text_padding'])

                add_circle_outline(draw, solution, min(sizing['circle_radius'], 78), ann['solution_color'], sizing['border_width'])
                add_smart_text_box(draw, (solution[0] - 52, solution[1] - 86), ann['solution_text'], font_size, ann['solution_color'], sizing['text_padding'])
            
            elif ann_type == 'heatmap_dual_risk':
                overstock = pct_to_px(ann['overstock_pct'])
                stockout = pct_to_px(ann['stockout_pct'])

                add_circle_outline(draw, overstock, min(sizing['circle_radius'], 78), ann['problem_color'], sizing['border_width'])
                add_smart_text_box(draw, (overstock[0] - 52, overstock[1] + 68), ann['overstock_text'], font_size, ann['problem_color'], sizing['text_padding'])

                add_circle_outline(draw, stockout, min(sizing['circle_radius'], 78), ann['solution_color'], sizing['border_width'])
                add_smart_text_box(draw, (stockout[0] - 52, stockout[1] - 92), ann['stockout_text'], font_size, ann['solution_color'], sizing['text_padding'])
            
            # VERTICAL GAP / TIME PERIOD
            elif ann_type == 'vertical_gap':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                top = pct_to_px(ann['top_pct'])
                bottom = pct_to_px(ann['bottom_pct'])

                draw.rectangle([left, top, right, bottom], outline=color, width=sizing['border_width'])

                mid_x = (left + right) // 2
                text = ann.get('text', '')
                add_smart_text_box(draw, (mid_x - 36, (top + bottom) // 2 - 32), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'time_period_region':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])

                draw.rectangle([left, int(height * 0.24), right, int(height * 0.76)], outline=color, width=sizing['border_width'])

                text = ann.get('text', '')
                add_smart_text_box(draw, ((left + right) // 2 - 42, int(height * 0.12)), text, font_size, color, sizing['text_padding'])
            
            # DIRECTION ARROWS
            elif ann_type in ['impact_arrow_down', 'lag_arrow_down', 'growth_arrow_up']:
                pos = pct_to_px(ann['position_pct'])
                direction = 'down' if 'down' in ann_type else 'up'
                arrow_len = max(60, int(height * 0.08))

                if direction == 'up':
                    end = (pos[0], pos[1] - arrow_len)
                else:
                    end = (pos[0], pos[1] + arrow_len)

                add_arrow_with_head(draw, pos, end, color, sizing['arrow_width'] + 1)

                text = ann.get('text', '')
                text_y = end[1] - int(height * 0.06) if direction == 'up' else end[1] + int(height * 0.02)
                add_smart_text_box(draw, (pos[0] - 50, text_y), text, font_size, color, sizing['text_padding'])
            
            # SCATTER/BOX
            elif ann_type == 'boxplot_span_bracket':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                bracket_y = pct_to_px(ann['bracket_y_pct'])
                
                bracket_h = sizing['bracket_height'] + 10
                draw.line([(left, bracket_y), (left, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(right, bracket_y), (right, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                draw.line([(left, bracket_y - bracket_h), (right, bracket_y - bracket_h)], fill=color, width=sizing['border_width'])
                
                text = ann.get('text', '')
                add_smart_text_box(draw, ((left + right) // 2 - 80, bracket_y - bracket_h - 80), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'scatter_optimal_point':
                center = pct_to_px(ann['center_pct'])
                add_circle_outline(draw, center, sizing['circle_radius'], color, sizing['border_width'] + 1)
                
                text = ann.get('text', '')
                add_smart_text_box(draw, (center[0] - 50, center[1] - 120), text, font_size, color, sizing['text_padding'])
            
            # QUADRANT LABELS
            elif ann_type in ['quadrant_star', 'quadrant_bait']:
                pos = pct_to_px(ann['position'])
                text = ann.get('text', '')
                draw.rectangle([pos[0] - 70, pos[1] - 50, pos[0] + 70, pos[1] + 80], fill='white', outline=color, width=sizing['border_width'])
                add_smart_text_box(draw, (pos[0] - 60, pos[1] - 40), text, font_size, color, sizing['text_padding'] - 2)
            
            # CURVE ZONES
            elif ann_type == 'curve_dual_zone':
                opt_left = pct_to_px(ann['optimal_left_pct'])
                opt_right = pct_to_px(ann['optimal_right_pct'])
                dim_left = pct_to_px(ann['diminishing_left_pct'])
                dim_right = pct_to_px(ann['diminishing_right_pct'])
                
                draw.rectangle([opt_left, int(height * 0.2), opt_right, int(height * 0.8)], outline=ann['optimal_color'], width=sizing['border_width'] + 1)
                add_smart_text_box(draw, ((opt_left + opt_right) // 2 - 70, int(height * 0.05)), ann['optimal_text'], font_size, ann['optimal_color'], sizing['text_padding'])
                
                draw.rectangle([dim_left, int(height * 0.2), dim_right, int(height * 0.8)], outline=ann['diminishing_color'], width=sizing['border_width'] + 1)
                add_smart_text_box(draw, ((dim_left + dim_right) // 2 - 50, int(height * 0.05)), ann['diminishing_text'], font_size, ann['diminishing_color'], sizing['text_padding'])
            
            # DIVERGING / WARNING LABELS
            elif ann_type == 'diverging_trend':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text_box(draw, (pos[0] - 70, pos[1] - 70), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'warning_label':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text_box(draw, (pos[0] - 50, pos[1] - 50), text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'seasonal_label':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text_box(draw, pos, text, font_size, color, sizing['text_padding'])
            
            elif ann_type == 'bar_revenue_premium':
                left_pos = pct_to_px(ann['left_position_pct'])
                right_pos = pct_to_px(ann['right_position_pct'])
                
                draw.rectangle([left_pos[0] - 50, left_pos[1] - 100, left_pos[0] + 50, left_pos[1]], outline='#999', width=sizing['border_width'])
                draw.rectangle([right_pos[0] - 50, right_pos[1] - 120, right_pos[0] + 50, right_pos[1]], outline='#2D5016', width=sizing['border_width'] + 1)
                
                add_smart_text_box(draw, (left_pos[0] - 40, left_pos[1] + 20), ann['left_text'], font_size - 2, '#999', sizing['text_padding'] - 2)
                add_smart_text_box(draw, (right_pos[0] - 40, right_pos[1] + 20), ann['right_text'], font_size - 2, '#2D5016', sizing['text_padding'] - 2)
        
        img_annotated.save(image_path)
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("=" * 90)
    print("🎨 OPTIMIZED FIGURE ANNOTATION - DYNAMIC SIZING & TYPOGRAPHY")
    print("=" * 90)
    
    success = 0
    fail = 0
    
    for rel_path, config in ADVANCED_ANNOTATIONS.items():
        full_path = os.path.join(FIGURES_DIR, rel_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  {config['name']:<50} SKIP")
            fail += 1
            continue
        
        critical = "🔴" if config.get('critical_finding') else "⚪"
        print(f"\n{critical} {config['name']:<48} ({len(config['annotations'])} annotations)")
        
        if annotate_figure(full_path, config['annotations']):
            print(f"   ✅ Optimized with dynamic sizing")
            success += 1
        else:
            fail += 1
    
    print("\n" + "=" * 90)
    print(f"✅ COMPLETE: {success} figures annotated with optimal sizing")
    if fail > 0:
        print(f"⚠️  {fail} skipped")
    print("=" * 90)


if __name__ == '__main__':
    main()
