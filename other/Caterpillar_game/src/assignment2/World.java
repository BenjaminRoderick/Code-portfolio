package assignment2;

public class World {
    private Caterpillar caterpillar;
    private Position foodPos;
    private Region map;
    private ActionQueue actionQueue;
    private TargetQueue targetQueue;
    private GameState gameState;
    public World(TargetQueue targets, ActionQueue actions){
        this.caterpillar = new Caterpillar();
        this.map = new Region(0,0,15,15);
        this.actionQueue = actions;
        this.targetQueue = targets;
        this.gameState = GameState.MOVE;
        this.foodPos = this.targetQueue.dequeue();
    }
    public void step(){
        Direction heading = null;

        if(actionQueue.isEmpty()){//first
            this.gameState = GameState.NO_MORE_ACTION;
        } else {
            heading = actionQueue.dequeue();
        }

        if(this.gameState != GameState.MOVE && this.gameState != GameState.EAT){//second
            return;
        }

        Position curr = new Position(this.caterpillar.getHead());//determine direction
        if(heading == Direction.NORTH){
            curr.moveNorth();
        } else if (heading == Direction.SOUTH) {
            curr.moveSouth();
        } else if(heading == Direction.WEST){
            curr.moveWest();
        } else {
            curr.moveEast();
        }

        if(!this.map.contains(curr)){
            this.gameState = GameState.WALL_COLLISION;
        } else if(this.caterpillar.selfCollision(curr)){
            this.gameState = GameState.SELF_COLLISION;
        } else if(curr.equals(this.foodPos)){
            if(this.targetQueue.isEmpty()){
                this.gameState = GameState.DONE;
            } else {
                this.caterpillar.eat(curr);
                this.gameState = GameState.EAT;
            }
        } else {
            this.caterpillar.move(curr);
            this.gameState = GameState.MOVE;
        }
    }
    public GameState getState(){
        return this.gameState;
    }
    public Caterpillar getCaterpillar(){
        return this.caterpillar;
    }
    public Position getFood(){
        return this.foodPos;
    }
    public boolean isRunning(){
        if(this.gameState != GameState.MOVE && this.gameState != GameState.EAT){
            return false;
        }
        return true;
    }
}
