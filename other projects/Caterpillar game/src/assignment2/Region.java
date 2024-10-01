package assignment2;

public class Region {
    private int maxX;
    private int maxY;
    private int minX;
    private int minY;
    public Region(int minX, int minY, int maxX, int maxY){
        this.maxX = maxX;
        this.maxY = maxY;
        this.minX = minX;
        this.minY = minY;
    }
    public boolean contains(Position toCheck){
        int x = toCheck.getX();
        int y = toCheck.getY();
        boolean xCheck = (x >= this.minX) && (x <= this.maxX);
        boolean yCheck = (y >= this.minY) && (y <= this.maxY);
        return xCheck && yCheck;
    }
}
