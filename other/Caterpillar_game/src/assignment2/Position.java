package assignment2;

public class Position {
    private int xPosition;
    private int yPosition;
    public Position(int x, int y){
        this.xPosition = x;
        this.yPosition = y;
    }
    public Position(Position pos){
        this.xPosition = pos.xPosition;
        this.yPosition = pos.yPosition;
    }
    public void reset(int newX, int newY){
        this.xPosition = newX;
        this.yPosition = newY;
    }
    public void reset(Position newPos){
        this.xPosition = newPos.xPosition;
        this.yPosition = newPos.yPosition;
    }
    public static int getDistance(Position a, Position b){
        return Math.abs(a.xPosition - b.xPosition) + Math.abs(a.yPosition - b.yPosition);
    }
    public int getX(){
        return this.xPosition;
    }
    public int getY(){
        return this.yPosition;
    }
    public void moveWest(){
        this.xPosition -= 1;
    }
    public void moveEast(){
        this.xPosition += 1;
    }
    public void moveNorth(){
        this.yPosition -= 1;
    }
    public void moveSouth(){
        this.yPosition += 1;
    }
    public boolean equals(Object a){
        if(!(a instanceof Position)){
            return false;
        }
        Position pos = (Position) a;
        if(pos.yPosition == this.yPosition && pos.xPosition == this.xPosition){
            return true;
        }
        return false;
    }
}
