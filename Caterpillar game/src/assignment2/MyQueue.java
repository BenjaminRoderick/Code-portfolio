package assignment2;

public class MyQueue<E> {
    private MyDoublyLinkedList<E> queueElements;
    public MyQueue(){
        this.queueElements = new MyDoublyLinkedList<E>();
    }
    public void enqueue(E toAdd){
        this.queueElements.addLast(toAdd);
    }
    public E dequeue(){
        return this.queueElements.removeFirst();
    }
    public boolean isEmpty(){
        return this.queueElements.isEmpty();
    }
    public void clear(){
        this.queueElements.clear();
    }
    public boolean equals(Object toCompare){
        if(!(toCompare instanceof MyQueue)){
            return false;
        }
        MyDoublyLinkedList<?> toCompareDLL = ((MyQueue<?>) toCompare).queueElements;
        return this.queueElements.equals(toCompareDLL);
    }
}
