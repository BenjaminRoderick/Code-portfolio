package assignment2;

public class TargetQueue extends MyQueue<Position>{
    private MyStack<String> stringStack;
    public TargetQueue(){
        super();
        this.stringStack = new MyStack<>();
    }
    public void clear(){
        super.clear();
        this.stringStack = null;
    }
    public void addTargets(String targets){
        String num = "";
        char curr;
        int a;
        int b;

        for(int i =0; i<targets.length(); i++){
            curr = targets.charAt(i);

            if(curr == '('){
                if(this.stringStack.getSize() != 0 || num != ""){
                    throw new IllegalArgumentException("Syntax of string is incorrect");
                }
                this.stringStack.push("(");

            } else if (Character.isDigit(curr)) {
                if(num.length() == 0 && this.stringStack.getSize() == 1) {
                    if (!this.stringStack.peek().equals("(")) {
                        throw new IllegalArgumentException("Syntax of string is incorrect");
                    }
                } else if(this.stringStack.getSize() == 3){
                    if(!this.stringStack.peek().equals(",")){
                        throw new IllegalArgumentException("Syntax of string is incorrect");
                    }
                }

                num += curr;

            } else if (curr == ',') {
                if(this.stringStack.getSize() == 1){
                    this.stringStack.push(num);
                    this.stringStack.push(",");
                    num = "";
                }
                else throw new IllegalArgumentException("Syntax of string is incorrect");

            } else if (curr == ')') {
                if(this.stringStack.getSize() != 3 || !this.stringStack.pop().equals(",")){
                    throw new IllegalArgumentException("Syntax of string is incorrect");
                }
                a = Integer.parseInt(this.stringStack.pop());
                b = Integer.parseInt(num);

                this.enqueue(new Position(a,b));

                num = "";
                this.stringStack.push(".");

            } else if(curr == '.'){
                if(i == 0){
                    continue;
                } else if(this.stringStack.isEmpty()){
                    throw new IllegalArgumentException("Syntax of string is incorrect");
                } else if(!this.stringStack.peek().equals(".")){
                    throw new IllegalArgumentException("Syntax of string is incorrect");
                }
                this.stringStack.clear();
            } else throw new IllegalArgumentException("Syntax of string is incorrect");
        }
        if(num.length() != 0 && this.isEmpty()){
            throw new IllegalArgumentException("Syntax of string is incorrect");
        }
    }

}
