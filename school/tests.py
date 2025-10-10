# from django.test import TestCase

# # Create your tests here.


# def generate_receipt(request, payment_id):
#     payment = get_object_or_404(Payment, id=payment_id)
#     athletes = payment.athletes.all()
#     athlete_count = athletes.count()
#     unit_price = Decimal("3000")
#     flat_fee = Decimal("500")
#     subtotal = unit_price * athlete_count
#     total = subtotal + flat_fee

#     # Setup PDF
#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
    
#     # Set margins
#     left_margin = 0.5 * inch
#     top_margin = height - 0.5 * inch
#     line_height = 14
    
#     # Logo and Company Info Header
#     try:
#         # Draw logo (adjust path to your actual logo file)
#         logo_path = "https://reg.usssaonline.com/static/lib/images/logo-receipt-01.png"  # Replace with your logo path
#         logo_width = 1.5 * inch
#         logo_height = 0.95 * inch
#         p.drawImage(logo_path, left_margin, top_margin - logo_height + 10, 
#                    width=logo_width, height=logo_height, preserveAspectRatio=True)
        
#         # Company info to the right of logo
#         company_info_x = left_margin + 1.25 * inch
#         p.setFont("Helvetica-Bold", 14)
#         p.setFillColorRGB(1.0, 0.0, 0.0)  # Dark blue color for title
#         p.drawString(company_info_x, top_margin, "UGANDA SECONDARY SCHOOLS SPORTS ASSOCIATION")
#         p.setFont("Helvetica", 10)
#         top_margin -= line_height
#         p.drawString(company_info_x, top_margin, "GNS PLAZA, OLD K'LA ROAD")
#         top_margin -= line_height
#         p.drawString(company_info_x, top_margin, "114052 KAMPALA UGANDA")
#         top_margin -= line_height
#         p.drawString(company_info_x, top_margin, "(256) 393-256054 | info@usssaonline.com")
#         top_margin -= line_height
#         p.drawString(company_info_x, top_margin, "www.usssaonline.com")
        
#         # Adjust top margin to account for logo height
#         top_margin = min(top_margin, height - 0.5 * inch - logo_height - 10)
#     except:
#         # Fallback if logo fails to load
#         p.setFont("Helvetica-Bold", 14)
#         p.setFillColorRGB(0.2, 0.2, 0.6)  # Dark blue
#         p.drawString(left_margin, top_margin, "UGANDA SECONDARY SCHOOLS SPORTS ASSOCIATION")
#         p.setFont("Helvetica", 10)
#         top_margin -= line_height
#         p.drawString(left_margin, top_margin, "GNS PLAZA, OLD K'LA ROAD")
#         top_margin -= line_height
#         p.drawString(left_margin, top_margin, "114052 KAMPALA UGANDA")
#         top_margin -= line_height
#         p.drawString(left_margin, top_margin, "(256) 393-256054 | info@usssaonline.com")
#         top_margin -= line_height
#         p.drawString(left_margin, top_margin, "www.usssaonline.com")
    
#     # Divider line
#     top_margin -= line_height * 2.5
#     # p.line(left_margin, top_margin, width - left_margin, top_margin)/
#     top_margin -= line_height
    
    
#     # Reset to black for subsequent text
#     p.setFillColorRGB(0, 0, 0)
    
#     # Recipient Info
#     p.setFont("Helvetica-Bold", 12)
#     p.setFillColorRGB(0.4, 0.4, 0.4)  # Dark gray for date
#     p.drawString(left_margin, top_margin, "RECIPIENT:")
#     top_margin -= line_height
#     p.setFont("Helvetica", 10)
#     p.drawString(left_margin, top_margin, payment.school.name)
#     top_margin -= line_height
#     p.drawString(left_margin, top_margin, f"Address: {payment.school.district.zone} {payment.school.district}")
#     top_margin -= line_height
#     p.drawString(left_margin, top_margin, f"Phone: {payment.phone_number}")
    
#     # Divider line
#     top_margin -= line_height * 2.5
#     # p.line(left_margin, top_margin, width - left_margin, top_margin)/
#     top_margin -= line_height
    
#     # Receipt Title
# # Receipt Title (Right-aligned)
#     p.setFont("Helvetica-Bold", 14)
#     receipt_title = f"Receipt for #{payment.transaction_id or 'N/A'}"
#     # Calculate width of text to right-align it
#     title_width = p.stringWidth(receipt_title, "Helvetica-Bold", 14)
#     p.drawString(width - left_margin - title_width, top_margin, receipt_title)
#     top_margin -= line_height * 2

#     p.setFont("Helvetica", 10)
#     date_text = f"Transaction Date: {payment.created_at.strftime('%B %d, %Y')}"
#     # Calculate width of date text to right-align it
#     date_width = p.stringWidth(date_text, "Helvetica", 10)
#     p.drawString(width - left_margin - date_width, top_margin, date_text)
#     top_margin -= line_height * 2

#     p.setFont("Helvetica", 10)
#     date_text = f"Transaction Date: {payment.created_at.strftime('%B %d, %Y')}"
#     # Calculate width of date text to right-align it
#     date_width = p.stringWidth(date_text, "Helvetica", 10)
#     p.drawString(width - left_margin - date_width, top_margin, date_text)
#     top_margin -= line_height * 2

#     p.setFont("Helvetica", 10)
#     date_text = f"Transaction Date: {payment.created_at.strftime('%B %d, %Y')}"
#     # Calculate width of date text to right-align it
#     date_width = p.stringWidth(date_text, "Helvetica", 10)
#     p.drawString(width - left_margin - date_width, top_margin, date_text)
#     top_margin -= line_height * 2
    
#     # Table Header
#     p.setFont("Helvetica-Bold", 10)
#     col_positions = [left_margin, left_margin + 2*inch, left_margin + 4*inch, left_margin + 5*inch, left_margin + 6*inch]
#     p.drawString(col_positions[0], top_margin, "SERVICE")
#     p.drawString(col_positions[1], top_margin, "DESCRIPTION")
#     p.drawString(col_positions[2], top_margin, "QTY.")
#     p.drawString(col_positions[3], top_margin, "COST")
#     p.drawString(col_positions[4], top_margin, "TOTAL")
#     top_margin -= line_height
#     p.line(left_margin, top_margin, width - left_margin, top_margin)
#     top_margin -= line_height
    
#     # Table Row 1: Athlete Registration
#     p.setFont("Helvetica", 10)
#     p.drawString(col_positions[0], top_margin, "Athlete Registration")
#     p.drawString(col_positions[1], top_margin, "Registration fees")
#     p.drawString(col_positions[2], top_margin, str(athlete_count))
#     p.drawString(col_positions[3], top_margin, f"UGX {unit_price:,.2f}")
#     p.drawString(col_positions[4], top_margin, f"UGX {subtotal:,.2f}")
#     top_margin -= line_height
    
#     # Athlete Names (as description)
#     for athlete in athletes:
#         name = f"- {athlete.fname} {athlete.lname}"
#         if top_margin < 1 * inch:  # Check if we need a new page
#             p.showPage()
#             top_margin = height - 1 * inch
#         p.drawString(col_positions[1], top_margin, name)
#         top_margin -= line_height
    
    
#         # Divider line
#     top_margin -= line_height * 1.5
#     # p.line(left_margin, top_margin, width - left_margin, top_margin)/
#     p.line(left_margin, top_margin, width - left_margin, top_margin)
#     top_margin -= line_height
    
#     # Table Row 2: Processing Fee
#     if top_margin < 1 * inch:
#         p.showPage()
#         top_margin = height - 0.5 * inch
    
#     p.drawString(col_positions[0], top_margin, "Processing Fee")
#     p.drawString(col_positions[1], top_margin, "Transaction processing fee")
#     p.drawString(col_positions[2], top_margin, "1")
#     p.drawString(col_positions[3], top_margin, f"UGX {flat_fee:,.2f}")
#     p.drawString(col_positions[4], top_margin, f"UGX {flat_fee:,.2f}")
#     top_margin -= line_height * 2
    
#     # Payment Summary
#     p.setFont("Helvetica", 10)
#     p.drawRightString(width - left_margin - 2*inch, top_margin, "Subtotal:")
#     p.drawRightString(width - left_margin, top_margin, f"UGX {subtotal:,.2f}")
#     top_margin -= line_height
    

    
#     p.setFont("Helvetica-Bold", 10)
#     p.setFillColorRGB( 0.0, 0.0, 0.502)  # Dark gray for date
#     p.drawRightString(width - left_margin - 2*inch, top_margin, "Total:")
#     p.drawRightString(width - left_margin, top_margin, f"UGX {total:,.2f}")
#     top_margin -= line_height * 3
    
#         # Reset to black for subsequent text
#     p.setFillColorRGB(0, 0, 0)
#     # Footer
#     p.setFont("Helvetica", 10)
#     p.setFillColorRGB(1.0, 0.0, 0.0)  # Dark blue color for title
#     p.drawString(left_margin, top_margin, "Thanks for your business!")
#     top_margin -= line_height * 2
    
#     # Powered by (optional)
#     p.setFont("Helvetica", 8)
#     p.drawString(left_margin, top_margin, "POWERED BY")
#     p.setFont("Helvetica-Bold", 8)
#     p.drawString(left_margin + 0.9 * inch, top_margin, "USSSA FINANCE SYSTEM")
    
#     # Finish
#     p.showPage()
#     p.save()
#     buffer.seek(0)

#     return FileResponse(buffer, as_attachment=True, filename=f'receipt_{payment.transaction_id}.pdf')


