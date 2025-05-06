package webapp;

import javax.servlet.*;
import java.io.*;

public class WebApplication extends HttpServlet {
    @Override
    public void init() throws ServletException {}

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html; charset=UTF-8");
        PrintWriter out = response.getWriter();

        // Inclua o JSP para exibir a página de mapa.
        out.println("<html>");
        out.println("<head><title>Heatmap Map</title></head>");
        out.println("<body>");
        out.println("<img src=\"/images/heatmap.png\">"); // Incluição do arquivo png;
        out.println("</body>");
        out.println("</html>");

        out.close();
    }
}