package assignment2;

public class ActionQueue extends MyQueue<Direction> {
    public ActionQueue(){
        super();
    }
    public void clear(){
        super.clear();
    }
    public void loadFromEncodedString(String message) {
        char curr;
        int bracketDepth = 0;
        char prev = 'a';
        String tempActions = "";
        String finalOut = "";
        String coeffList = "";

        for(int i = 0; i < message.length(); i++) {
            curr = message.charAt(i);

            if(Character.isDigit(curr)){
                if(Character.isDigit(prev)){
                    coeffList += curr;
                } else if(prev != 'a' && prev != ']'){
                    throw new IllegalArgumentException("Syntax Error: " + prev + " before " + curr);
                } else {
                    coeffList += curr;
                }
            }else if(curr == 'N'){
                if(!this.prevCheck(prev)){
                    throw new IllegalArgumentException("Syntax Error: Missing [");
                }
                tempActions += "N";
            } else if(curr == 'S'){
                if(!this.prevCheck(prev)){
                    throw new IllegalArgumentException("Syntax Error: Missing [");
                }
                tempActions += "S";

            } else if(curr == 'E'){
                if(!this.prevCheck(prev)){
                    throw new IllegalArgumentException("Syntax Error: Missing [");
                }
                tempActions += "E";
            } else if(curr == 'W'){
                if(!this.prevCheck(prev)){
                    throw new IllegalArgumentException("Syntax Error: Missing [");
                }
                tempActions += "W";
            } else if(curr == '['){
                if(i != 0 && !Character.isDigit(prev)){
                    throw new IllegalArgumentException("Syntax Error: Missing K");
                }
                bracketDepth += 1;
            } else if(curr == ']'){
                if(bracketDepth == 0){
                    throw new IllegalArgumentException("Syntax Error: Missing [");
                }
                if(bracketDepth == 1){
                    int multiply = Integer.parseInt(coeffList);
                    for(int j = 0; j < multiply; j++){
                        finalOut += tempActions;
                    }
                    coeffList = "";
                    tempActions = "";
                    bracketDepth -= 1;
                }
                //*
                //add the code for more than depth 1 brackets here
                //*
            }

            prev = curr;
        }
        for(int i = 0; i < finalOut.length(); i++){
            curr = finalOut.charAt(i);
            if(curr == 'N'){
                this.enqueue(Direction.NORTH);
            } else if (curr == 'S'){
                this.enqueue(Direction.SOUTH);
            } else if(curr == 'E'){
                this.enqueue(Direction.EAST);
            } else if(curr == 'W'){
                this.enqueue(Direction.WEST);
            }
        }
    }
    private boolean prevCheck(char prev){
        boolean direction = false;
        for(char i: new char[]{'N','S','E','W'}){
            if(prev == i){
                direction = true;
                break;
            }
        }
        return prev == '[' || direction;
    }

}
