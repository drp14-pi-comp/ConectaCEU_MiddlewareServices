"""PDF rendering service - converts HTML to PDF"""
from typing import Optional
from weasyprint import HTML

class PdfRenderService:
    """Service for rendering PDF documents from HTML"""
    
    @staticmethod
    def render_from_html(html_content: str, base_url: Optional[str] = None) -> bytes:
        """
        Convert HTML string to PDF bytes.
        
        Args:
            html_content: HTML string to render
            base_url: Optional base URL for resolving relative paths (images, CSS)
            
        Returns:
            PDF as bytes
        """
        doc = HTML(string=html_content, base_url=base_url)
        return doc.write_pdf()