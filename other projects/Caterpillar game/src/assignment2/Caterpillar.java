package assignment2;

public class Caterpillar extends MyDoublyLinkedList<Position>{
    public Caterpillar(){
        super();
        this.addLast(new Position(7,7));
    }
    public Position getHead(){
        return this.peekFirst();
    }
    public void eat(Position toAdd){
        if(!checkAdjacent(this.getHead(), toAdd)){
            throw new IllegalArgumentException("Input Position is not adjacent to head Position");
        }
        this.addFirst(toAdd);
    }
    public void move(Position toAdd){
        if(!checkAdjacent(this.getHead(), toAdd)){
            throw new IllegalArgumentException("Input Position is not adjacent to head Position");
        }
        this.addFirst(toAdd);
        this.removeLast();
    }
    public boolean selfCollision(Position checkPos){
        boolean collisionFound = false;

        for(Position curr: this){
            if(curr.equals(checkPos)){
                collisionFound = true;
                break;
            }
        }
        return collisionFound;
    }
    private static boolean checkAdjacent(Position currPos, Position nextPos){
        boolean match = false;
        Position a = new Position(currPos);
        Position b = new Position(currPos);
        Position c = new Position(currPos);
        Position d = new Position(currPos);
        a.moveSouth();
        b.moveNorth();
        c.moveWest();
        d.moveEast();
        Position[] adjacent = {a,b,c,d};

        for(Position i: adjacent){
            if(nextPos.equals(i)){
                match = true;
                break;
            }
        }
        return match;
    }
}
