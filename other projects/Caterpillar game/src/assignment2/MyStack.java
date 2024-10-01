package assignment2;

public class MyStack<E> {
    private MyDoublyLinkedList<E> stackElements;
    public MyStack(){
        this.stackElements = new MyDoublyLinkedList<E>();
    }
    public void push(E toAdd){
        this.stackElements.addLast(toAdd);
    }
    public E pop(){
        return this.stackElements.removeLast();
    }
    public E peek(){
        return this.stackElements.peekLast();
    }
    public boolean isEmpty(){
        return this.stackElements.isEmpty();
    }
    public void clear(){
        this.stackElements.clear();
    }
    public int getSize(){
        return this.stackElements.getSize();
    }
}
