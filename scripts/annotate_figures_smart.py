#!/usr/bin/env python3
"""
Intelligent figure annotation with optimal placement based on chart type.
Uses analysis of actual figure dimensions to place annotations thoughtfully.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

FIGURES_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'

# Intelligent annotations with chart-type-aware positioning
SMART_ANNOTATIONS = {
    # ============================================================================
    # CATEGORY 01: Product & Market Dominance
    # ============================================================================
    
    '01_product_market_dominance/category_pie.png': {
        'name': 'Streetwear Monopoly (Pie Chart)',
        'chart_type': 'pie',
        'annotations': [
            {
                'type': 'pie_slice_highlight',
                'angle_start': 0,
                'angle_end': 290,  # ~80% of circle
                'text': '80% STREETWEAR\n486K units',
                'color': '#CE2626',
                'radius_pct': 65
            }
        ]
    },
    
    '01_product_market_dominance/segment_market_share_new.png': {
        'name': 'Market Share Trend (Line Chart)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'trend_arrow',
                'start_pct': (75, 30),
                'end_pct': (90, 55),
                'text': 'Declining\nGrowth',
                'color': '#CE2626',
                'text_offset': (10, 5)
            }
        ]
    },
    
    '01_product_market_dominance/margin_by_size.png': {
        'name': 'Size Profitability (Grouped Bar Chart)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'bar_group_highlight',
                'left_pct': 75,  # L/XL bars (right side)
                'right_pct': 95,
                'y_middle_pct': 35,
                'text': 'Premium\nMargin\n30-35%',
                'color': '#2D5016',
                'style': 'box'
            },
            {
                'type': 'bar_group_highlight',
                'left_pct': 20,  # S/M bars (left side)
                'right_pct': 40,
                'y_middle_pct': 60,
                'text': 'Commodity\nMargin\n18-26%',
                'color': '#CE2626',
                'style': 'box'
            },
            {
                'type': 'margin_gap_bracket',
                'left_pct': 10,
                'right_pct': 10,
                'top_pct': 15,
                'text': '12-17pp\nGap',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_new.png': {
        'name': 'Profitability by Size (Scatter/Box)',
        'chart_type': 'scatter',
        'annotations': [
            {
                'type': 'vertical_gap_indicator',
                'left_pct': 75,
                'right_pct': 90,
                'top_pct': 25,
                'bottom_pct': 70,
                'text': 'Gap:\n12-17pp',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/size_profitability_boxplot.png': {
        'name': 'Size Distribution (Boxplot)',
        'chart_type': 'box',
        'annotations': [
            {
                'type': 'boxplot_span_bracket',
                'left_label': 'S/M',
                'right_label': 'L/XL',
                'left_pct': 20,
                'right_pct': 80,
                'bracket_y_pct': 10,
                'text': 'Premium Size Advantage: 12-17pp',
                'color': '#CE2626'
            }
        ]
    },
    
    '01_product_market_dominance/monthly_trend_heatmap.png': {
        'name': 'Monthly Seasonality (Heatmap)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'heatmap_cell_highlight',
                'col_pct': 42,  # May (month 5, roughly center)
                'text': 'May Peak\n2.6x',
                'color': '#2D5016',
                'arrow_to': (42, 50)
            }
        ]
    },
    
    '01_product_market_dominance/star_vs_bait_analysis.png': {
        'name': 'Portfolio Analysis (Multi-region)',
        'chart_type': 'scatter',
        'annotations': [
            {
                'type': 'quadrant_label',
                'position': (80, 25),
                'text': 'STAR (UR)\n31.3% Margin',
                'color': '#2D5016'
            },
            {
                'type': 'quadrant_label',
                'position': (20, 75),
                'text': 'BAIT (YY/UC)\n23-24% Margin',
                'color': '#CE2626'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 02: Customer Lifecycle & Acquisition
    # ============================================================================
    
    '02_customer_lifecycle_acquisition/cohort_growth.png': {
        'name': 'Cohort Retention Trend (Line Chart)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'line_decline_arrow',
                'start_pct': (15, 25),
                'end_pct': (85, 80),
                'text': 'Retention\nCollapse\n40%→10%',
                'color': '#CE2626',
                'curve': True
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/repeat_rate_by_channel.png': {
        'name': 'Channel Comparison (Grouped Bar)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'bar_highlight',
                'position_pct': (25, 50),
                'height_pct': 38,
                'text': 'Organic\n38%',
                'color': '#2D5016'
            },
            {
                'type': 'bar_highlight',
                'position_pct': (70, 70),
                'height_pct': 8,
                'text': 'Double-Day\n8%',
                'color': '#CE2626'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_by_channel.png': {
        'name': 'LTV Variation (Bar Chart)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'bar_group_span_bracket',
                'left_pct': 15,
                'right_pct': 40,
                'bracket_y_pct': 5,
                'text': 'High LTV (Sustainable)',
                'color': '#2D5016'
            },
            {
                'type': 'bar_group_span_bracket',
                'left_pct': 65,
                'right_pct': 85,
                'bracket_y_pct': 5,
                'text': 'Low LTV (Loss-making)',
                'color': '#CE2626'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/ltv_demographics_heatmap.png': {
        'name': 'Demographics Heatmap (Heat Map)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'heatmap_hotspot',
                'center_pct': (80, 30),
                'size': 'large',
                'text': 'High-Value\nSegment',
                'color': '#2D5016'
            }
        ]
    },
    
    '02_customer_lifecycle_acquisition/acquisition_efficiency.png': {
        'name': 'CAC/LTV Trend (Dual Line)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'diverging_lines_label',
                'left_pct': (30, 35),
                'right_pct': (70, 50),
                'text': 'Diverging:\nCAC ↑ LTV ↓',
                'color': '#CE2626'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 03: Operational Friction & Leakage
    # ============================================================================
    
    '03_operational_friction_leakage/returns_bar.png': {
        'name': 'Return Reasons (Stacked Bar)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'bar_highlight_with_label',
                'position_pct': (35, 50),
                'label_offset': (5, 5),
                'text': 'Wrong Size\n34.6%\n(3.5pp margin loss)',
                'color': '#CE2626',
                'emphasis': 'high'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_deep_dive.png': {
        'name': 'Return Impact (Trend)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'impact_arrow',
                'position_pct': (50, 40),
                'direction': 'down',
                'text': 'Margin\nErosion\n3.5pp',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_friction_matrix.png': {
        'name': 'Return Rate Matrix (Heatmap)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'heatmap_region_contrast',
                'top_left_pct': (10, 10),
                'top_right_pct': (40, 35),
                'bottom_left_pct': (60, 60),
                'bottom_right_pct': (90, 90),
                'top_text': 'High Return\n(S/M)',
                'bottom_text': 'Low Return\n(L/XL)',
                'color_top': '#CE2626',
                'color_bottom': '#2D5016'
            }
        ]
    },
    
    '03_operational_friction_leakage/return_reason_matrix.png': {
        'name': 'Wrong-Size Hotspot (Heatmap)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'heatmap_hotspot_circle',
                'center_pct': (35, 25),
                'radius_pct': 15,
                'text': 'Wrong-Size\nHotspot',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/tet_holiday_friction.png': {
        'name': 'Post-Tết Delivery Failure (Time Series)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'time_period_highlight',
                'left_pct': 15,
                'right_pct': 40,
                'text': 'Post-Tết Surge\n8.2% Failure',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/seasonal_operational_patterns.png': {
        'name': 'Seasonal Pattern (Grouped)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'seasonal_region_label',
                'position_pct': (40, 30),
                'text': 'Post-Tết\nSurge',
                'color': '#CE2626'
            }
        ]
    },
    
    '03_operational_friction_leakage/inventory_risk_analysis.png': {
        'name': 'Inventory Risk (Heatmap)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'heatmap_dual_region',
                'problem_pct': (25, 65),
                'solution_pct': (75, 25),
                'problem_text': 'Overstock\nRisk',
                'solution_text': 'Stockout\nRisk',
                'problem_color': '#CE2626',
                'solution_color': '#2D5016'
            }
        ]
    },
    
    '03_operational_friction_leakage/shipping_delivery_efficiency.png': {
        'name': 'Delivery Lag (Time Series)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'peak_lag_indicator',
                'position_pct': (70, 35),
                'direction': 'down',
                'text': 'Peak\nDelay',
                'color': '#CE2626'
            }
        ]
    },
    
    # ============================================================================
    # CATEGORY 04: Financial Dynamics & Payment
    # ============================================================================
    
    '04_financial_payment_dynamics/payment_analysis.png': {
        'name': 'Payment Method Distribution (Pie)',
        'chart_type': 'pie',
        'annotations': [
            {
                'type': 'pie_slice_emphasis',
                'angle_start': 80,
                'angle_end': 240,  # ~22% slice
                'text': 'Installment\n22% Orders\n28% Revenue',
                'color': '#2D5016',
                'radius_pct': 60
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_aov_boxplot.png': {
        'name': 'AOV Lift Distribution (Box)',
        'chart_type': 'box',
        'annotations': [
            {
                'type': 'box_span_bracket',
                'left_pct': 25,
                'right_pct': 75,
                'bracket_y_pct': 10,
                'text': '+35% AOV Lift from Installment',
                'color': '#2D5016'
            }
        ]
    },
    
    '04_financial_payment_dynamics/installment_revenue_share.png': {
        'name': 'Revenue Premium (Grouped Bar)',
        'chart_type': 'bar',
        'annotations': [
            {
                'type': 'bar_comparison',
                'left_position_pct': (25, 50),
                'right_position_pct': (75, 65),
                'left_text': '22%\nOrders',
                'right_text': '28%\nRevenue',
                'left_color': '#999',
                'right_color': '#2D5016',
                'bracket_text': 'Premium Mix'
            }
        ]
    },
    
    '04_financial_payment_dynamics/monthly_installments_trend.png': {
        'name': 'Installment Adoption Trend (Line)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'growth_arrow',
                'position_pct': (75, 35),
                'direction': 'up',
                'text': 'Growth\nOpportunity\n(Currently 22%)',
                'color': '#2D5016'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promotion_impact.png': {
        'name': 'Optimal Discount Range (Curve)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'curve_region_highlight',
                'optimal_left_pct': 40,
                'optimal_right_pct': 65,
                'optimal_y_pct': 50,
                'diminishing_left_pct': 65,
                'diminishing_right_pct': 100,
                'diminishing_y_pct': 40,
                'optimal_text': 'Optimal\nZone\n15-25%',
                'diminishing_text': 'Diminishing\nReturns',
                'optimal_color': '#2D5016',
                'diminishing_color': '#CE2626'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_depth_volume.png': {
        'name': 'Volume Elasticity (Scatter)',
        'chart_type': 'scatter',
        'annotations': [
            {
                'type': 'optimal_point_circle',
                'center_pct': (50, 50),
                'radius_pct': 12,
                'text': 'Optimal\nPoint',
                'color': '#2D5016'
            }
        ]
    },
    
    '04_financial_payment_dynamics/promo_urgency_stackability.png': {
        'name': 'Competitive Pressure (Matrix)',
        'chart_type': 'heatmap',
        'annotations': [
            {
                'type': 'competitive_warning',
                'position_pct': (50, 50),
                'text': 'Race to\nBottom',
                'color': '#CE2626'
            }
        ]
    },
    
    '04_financial_payment_dynamics/revenue_margin_trend.png': {
        'name': 'Growth Paradox (Dual Line)',
        'chart_type': 'line',
        'annotations': [
            {
                'type': 'diverging_trend',
                'position_pct': (80, 50),
                'text': 'Revenue ↑\nMargin ↓',
                'color': '#CE2626'
            }
        ]
    },
}


def add_smart_text(draw, position, text, color='#CE2626', font_size=11, bg_color='white'):
    """Add text with smart background and sizing"""
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    padding = 8
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


def add_arrow(draw, start, end, color='#CE2626', width=3):
    """Add arrow with proper arrowhead"""
    draw.line([start, end], fill=color, width=width)
    
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


def add_circle(draw, center, radius, color='#CE2626', width=3):
    """Add circle outline"""
    x, y = center
    bbox = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(bbox, outline=color, width=width)


def annotate_figure(image_path, annotations):
    """Smart annotation based on chart type"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        img_annotated = img.copy()
        draw = ImageDraw.Draw(img_annotated, 'RGBA')
        
        for ann in annotations:
            ann_type = ann.get('type')
            color = ann.get('color', '#CE2626')
            
            def pct_to_px(pct_val):
                """Convert percentage to pixel coordinate"""
                if isinstance(pct_val, tuple):
                    return (int(width * pct_val[0] / 100), int(height * pct_val[1] / 100))
                return int(width * pct_val / 100) if pct_val <= 100 else int(pct_val)
            
            # Pie chart annotations
            if ann_type == 'pie_slice_highlight':
                center = (width // 2, height // 2)
                radius = min(width, height) * ann.get('radius_pct', 60) / 200
                # Draw circle on pie
                add_circle(draw, center, int(radius), color, width=4)
                # Add text outside
                text = ann.get('text', '')
                text_pos = (int(center[0] + radius + 50), int(center[1] - 50))
                add_smart_text(draw, text_pos, text, color, font_size=12)
                # Draw arrow from text to pie
                add_arrow(draw, text_pos, (int(center[0] + radius + 20), int(center[1])), color, width=2)
            
            elif ann_type == 'pie_slice_emphasis':
                center = (width // 2, height // 2)
                radius = min(width, height) * ann.get('radius_pct', 60) / 200
                add_circle(draw, center, int(radius * 0.8), color, width=4)
                text = ann.get('text', '')
                text_pos = (int(center[0] + radius + 40), int(center[1] - 80))
                add_smart_text(draw, text_pos, text, color, font_size=11)
                add_arrow(draw, text_pos, (int(center[0] + radius + 10), int(center[1] - 20)), color, width=2)
            
            # Bar chart annotations
            elif ann_type == 'bar_highlight':
                pos = pct_to_px(ann['position_pct'])
                height_px = pct_to_px(ann.get('height_pct', 30))
                # Draw box
                draw.rectangle([pos[0] - 40, pos[1] - height_px, pos[0] + 40, pos[1]], 
                             outline=color, width=3)
                # Add text above bar
                text = ann.get('text', '')
                add_smart_text(draw, (pos[0] - 30, pos[1] - height_px - 40), text, color, font_size=10)
            
            elif ann_type == 'bar_group_highlight':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                y_mid = pct_to_px(ann['y_middle_pct'])
                
                if ann.get('style') == 'box':
                    draw.rectangle([left, y_mid - 100, right, y_mid + 100], outline=color, width=3)
                
                text = ann.get('text', '')
                text_x = (left + right) // 2 - 40
                add_smart_text(draw, (text_x, y_mid - 60), text, color, font_size=10)
            
            elif ann_type == 'bar_group_span_bracket':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                bracket_y = pct_to_px(ann['bracket_y_pct'])
                
                # Draw bracket
                bracket_h = 20
                draw.line([(left, bracket_y), (left, bracket_y - bracket_h)], fill=color, width=2)
                draw.line([(right, bracket_y), (right, bracket_y - bracket_h)], fill=color, width=2)
                draw.line([(left, bracket_y - bracket_h), (right, bracket_y - bracket_h)], fill=color, width=2)
                
                text = ann.get('text', '')
                text_x = (left + right) // 2 - 60
                add_smart_text(draw, (text_x, bracket_y - bracket_h - 35), text, color, font_size=10)
            
            elif ann_type == 'bar_comparison':
                left_pos = pct_to_px(ann['left_position_pct'])
                right_pos = pct_to_px(ann['right_position_pct'])
                
                # Highlight bars
                draw.rectangle([left_pos[0] - 30, left_pos[1] - 80, left_pos[0] + 30, left_pos[1]], 
                             outline=ann.get('left_color', '#999'), width=2)
                draw.rectangle([right_pos[0] - 30, right_pos[1] - 100, right_pos[0] + 30, right_pos[1]], 
                             outline=ann.get('right_color', '#2D5016'), width=2)
                
                # Add labels
                add_smart_text(draw, (left_pos[0] - 25, left_pos[1] + 10), ann.get('left_text', ''), 
                             ann.get('left_color', '#999'), font_size=9)
                add_smart_text(draw, (right_pos[0] - 25, right_pos[1] + 10), ann.get('right_text', ''), 
                             ann.get('right_color', '#2D5016'), font_size=9)
            
            # Line chart annotations
            elif ann_type == 'trend_arrow':
                start = pct_to_px(ann['start_pct'])
                end = pct_to_px(ann['end_pct'])
                add_arrow(draw, start, end, color, width=4)
                
                text = ann.get('text', '')
                text_offset = ann.get('text_offset', (10, 5))
                text_pos = (end[0] + text_offset[0], end[1] + text_offset[1])
                add_smart_text(draw, text_pos, text, color, font_size=11)
            
            elif ann_type == 'line_decline_arrow':
                start = pct_to_px(ann['start_pct'])
                end = pct_to_px(ann['end_pct'])
                
                # Draw curved arrow
                add_arrow(draw, start, end, color, width=4)
                
                text = ann.get('text', '')
                mid_x = (start[0] + end[0]) // 2
                mid_y = (start[1] + end[1]) // 2
                add_smart_text(draw, (mid_x - 40, mid_y - 80), text, color, font_size=11)
            
            elif ann_type == 'diverging_lines_label':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                
                mid_x = (left[0] + right[0]) // 2
                mid_y = (left[1] + right[1]) // 2
                
                add_smart_text(draw, (mid_x - 40, mid_y), ann.get('text', ''), color, font_size=11)
            
            # Heatmap annotations
            elif ann_type == 'heatmap_cell_highlight':
                col_x = pct_to_px(ann['col_pct'])
                # Approximate cell position
                cell_size = int(width * 0.06)
                center = (col_x, height // 2)
                add_circle(draw, center, int(cell_size * 0.6), color, width=3)
                
                text = ann.get('text', '')
                add_smart_text(draw, (col_x - 40, height - 150), text, color, font_size=10)
            
            elif ann_type == 'heatmap_hotspot':
                center = pct_to_px(ann['center_pct'])
                radius = int(width * 0.08)
                add_circle(draw, center, radius, color, width=3)
                
                text = ann.get('text', '')
                add_smart_text(draw, (center[0] - 40, center[1] - 80), text, color, font_size=10)
            
            elif ann_type == 'heatmap_hotspot_circle':
                center = pct_to_px(ann['center_pct'])
                radius = int(width * ann.get('radius_pct', 15) / 100)
                add_circle(draw, center, radius, color, width=3)
                
                text = ann.get('text', '')
                add_smart_text(draw, (center[0] - 40, center[1] + radius + 20), text, color, font_size=10)
            
            elif ann_type == 'heatmap_region_contrast':
                top_left = pct_to_px((ann['top_left_pct'][0], ann['top_left_pct'][1]))
                top_right = pct_to_px((ann['top_right_pct'][0], ann['top_right_pct'][1]))
                bottom_right = pct_to_px((ann['bottom_right_pct'][0], ann['bottom_right_pct'][1]))
                
                # Top region (high return)
                draw.rectangle([top_left[0], top_left[1], top_right[0], top_right[1]], 
                             outline=ann['color_top'], width=3)
                add_smart_text(draw, (top_left[0] + 10, top_left[1] + 10), ann.get('top_text', ''), 
                             ann['color_top'], font_size=10)
                
                # Bottom region (low return)
                draw.rectangle([pct_to_px((ann['bottom_left_pct'][0], ann['bottom_left_pct'][1]))[0], 
                              pct_to_px((ann['bottom_left_pct'][0], ann['bottom_left_pct'][1]))[1],
                              bottom_right[0], bottom_right[1]], 
                             outline=ann['color_bottom'], width=3)
                add_smart_text(draw, (bottom_right[0] - 80, bottom_right[1] - 40), ann.get('bottom_text', ''), 
                             ann['color_bottom'], font_size=10)
            
            elif ann_type == 'heatmap_dual_region':
                problem_pos = pct_to_px(ann['problem_pct'])
                solution_pos = pct_to_px(ann['solution_pct'])
                
                add_circle(draw, problem_pos, 60, ann['problem_color'], width=3)
                add_smart_text(draw, (problem_pos[0] - 40, problem_pos[1] - 80), ann['problem_text'], 
                             ann['problem_color'], font_size=10)
                
                add_circle(draw, solution_pos, 60, ann['solution_color'], width=3)
                add_smart_text(draw, (solution_pos[0] - 40, solution_pos[1] - 80), ann['solution_text'], 
                             ann['solution_color'], font_size=10)
            
            # Time-based annotations
            elif ann_type == 'time_period_highlight':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                
                # Vertical region highlight
                draw.rectangle([left, int(height * 0.15), right, int(height * 0.85)], 
                             outline=color, width=3)
                
                text = ann.get('text', '')
                add_smart_text(draw, ((left + right) // 2 - 40, int(height * 0.1)), text, color, font_size=11)
            
            elif ann_type == 'seasonal_region_label':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text(draw, pos, text, color, font_size=11)
            
            # Scatter/Box annotations
            elif ann_type == 'vertical_gap_indicator':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                top = pct_to_px(ann['top_pct'])
                bottom = pct_to_px(ann['bottom_pct'])
                
                draw.rectangle([left, top, right, bottom], outline=color, width=3)
                
                mid_x = (left + right) // 2
                add_smart_text(draw, (mid_x - 25, (top + bottom) // 2 - 25), ann.get('text', ''), 
                             color, font_size=10)
            
            elif ann_type == 'boxplot_span_bracket':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                bracket_y = pct_to_px(ann['bracket_y_pct'])
                
                bracket_h = 25
                draw.line([(left, bracket_y), (left, bracket_y - bracket_h)], fill=color, width=2)
                draw.line([(right, bracket_y), (right, bracket_y - bracket_h)], fill=color, width=2)
                draw.line([(left, bracket_y - bracket_h), (right, bracket_y - bracket_h)], fill=color, width=2)
                
                text = ann.get('text', '')
                text_x = (left + right) // 2 - 80
                add_smart_text(draw, (text_x, bracket_y - bracket_h - 40), text, color, font_size=10)
            
            elif ann_type == 'box_span_bracket':
                left = pct_to_px(ann['left_pct'])
                right = pct_to_px(ann['right_pct'])
                bracket_y = pct_to_px(ann['bracket_y_pct'])
                
                # Bracket
                bracket_h = 30
                draw.line([(left, bracket_y), (left, bracket_y - bracket_h)], fill=color, width=3)
                draw.line([(right, bracket_y), (right, bracket_y - bracket_h)], fill=color, width=3)
                draw.line([(left, bracket_y - bracket_h), (right, bracket_y - bracket_h)], fill=color, width=3)
                
                text = ann.get('text', '')
                text_x = (left + right) // 2 - 80
                add_smart_text(draw, (text_x, bracket_y - bracket_h - 50), text, color, font_size=11)
            
            elif ann_type == 'optimal_point_circle':
                center = pct_to_px(ann['center_pct'])
                radius = int(width * ann.get('radius_pct', 12) / 100)
                add_circle(draw, center, radius, color, width=3)
                
                text = ann.get('text', '')
                add_smart_text(draw, (center[0] - 35, center[1] - radius - 60), text, color, font_size=11)
            
            elif ann_type == 'curve_region_highlight':
                # Optimal zone
                opt_left = pct_to_px(ann['optimal_left_pct'])
                opt_right = pct_to_px(ann['optimal_right_pct'])
                opt_y = pct_to_px(ann['optimal_y_pct'])
                
                draw.rectangle([opt_left, int(opt_y - 100), opt_right, int(opt_y + 100)], 
                             outline=ann['optimal_color'], width=3)
                add_smart_text(draw, ((opt_left + opt_right) // 2 - 35, opt_y - 120), 
                             ann['optimal_text'], ann['optimal_color'], font_size=10)
                
                # Diminishing returns zone
                dim_left = pct_to_px(ann['diminishing_left_pct'])
                dim_right = pct_to_px(ann['diminishing_right_pct'])
                dim_y = pct_to_px(ann['diminishing_y_pct'])
                
                draw.rectangle([dim_left, int(dim_y - 100), dim_right, int(dim_y + 100)], 
                             outline=ann['diminishing_color'], width=3)
                add_smart_text(draw, ((dim_left + dim_right) // 2 - 35, dim_y - 120), 
                             ann['diminishing_text'], ann['diminishing_color'], font_size=10)
            
            # Direction-based annotations
            elif ann_type == 'growth_arrow' or ann_type == 'impact_arrow' or ann_type == 'peak_lag_indicator':
                pos = pct_to_px(ann['position_pct'])
                direction = ann.get('direction', 'up')
                
                if direction == 'up':
                    end = (pos[0], pos[1] - 80)
                else:
                    end = (pos[0], pos[1] + 80)
                
                add_arrow(draw, pos, end, color, width=4)
                
                text = ann.get('text', '')
                text_y = end[1] - 60 if direction == 'up' else end[1] + 20
                add_smart_text(draw, (pos[0] - 40, text_y), text, color, font_size=11)
            
            # Quadrant/Region labels
            elif ann_type == 'quadrant_label':
                pos = pct_to_px(ann['position'])
                text = ann.get('text', '')
                # Add background box for clarity
                draw.rectangle([pos[0] - 50, pos[1] - 30, pos[0] + 50, pos[1] + 50], 
                             fill='white', outline=color, width=2)
                add_smart_text(draw, (pos[0] - 45, pos[1] - 20), text, color, font_size=11)
            
            elif ann_type == 'competitive_warning':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text(draw, (pos[0] - 40, pos[1] - 40), text, color, font_size=12)
            
            elif ann_type == 'diverging_trend':
                pos = pct_to_px(ann['position_pct'])
                text = ann.get('text', '')
                add_smart_text(draw, (pos[0] - 50, pos[1] - 50), text, color, font_size=11)
        
        # Save
        img_annotated.save(image_path)
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run smart annotation pipeline"""
    print("=" * 80)
    print("🎨 INTELLIGENT FIGURE ANNOTATION - SMART PLACEMENT")
    print("=" * 80)
    
    success = 0
    fail = 0
    
    for rel_path, config in SMART_ANNOTATIONS.items():
        full_path = os.path.join(FIGURES_DIR, rel_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  {config['name']:<50} SKIP (not found)")
            fail += 1
            continue
        
        print(f"\n✏️  {config['name']:<50} ({config['chart_type'].upper()})")
        
        if annotate_figure(full_path, config['annotations']):
            print(f"   ✅ {len(config['annotations'])} annotation(s) added")
            success += 1
        else:
            fail += 1
    
    print("\n" + "=" * 80)
    print(f"✅ COMPLETE: {success} figures annotated successfully")
    if fail > 0:
        print(f"⚠️  {fail} skipped")
    print("=" * 80)


if __name__ == '__main__':
    main()
