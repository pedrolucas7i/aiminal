package webapp.servlets;

import javax.servlet.*;
import java.io.*;
import java.util.ArrayList;
import java.util.List;

public class HeatmapServlet extends HttpServlet {
    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        // Adiciona o código para gerar o mapa no servlet.
        response.setContentType("text/html; charset=UTF-8");
        PrintWriter out = response.getWriter();

        List<String> data = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            data.add(String.valueOf(i));
        }
        out.println("<script src=\"https://js.arcgis.com/v4.21/"></script>");
        out.println("<div id=\"map\" style=\"width:800px;height:600px;\"></div>");
        out.println("<script>");
        out.println("var map = new esri.Map({view: esri.View2D, container: 'map'});");
        out.println("var featureLayer = new esri.FeatureLayer({url: \"https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_map/MapServer/0\"});");
        out.println("var heatmapOptions = {field: 1, maxScale: 10000, minOpacity: 0.2}");
        out.println("map.add(heatmapOptions)");
        out.println("map.setExtent(new esri.Extent({x: -108, y: 37, width: 2017, height: 83.6}));");
        out.println("</script>");
    }
}