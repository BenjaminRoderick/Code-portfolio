package assignment2;

public interface MyList<E> extends Iterable<E> {
    int getSize();
    boolean isEmpty();
    void add(E toAdd);
    void clear();
    E remove();
}
