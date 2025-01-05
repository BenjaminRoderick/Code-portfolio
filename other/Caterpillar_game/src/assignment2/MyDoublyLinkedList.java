package assignment2;

import java.util.Iterator;
import java.util.NoSuchElementException;

public class MyDoublyLinkedList<E> extends MyLinkedList<E> {
	private DNode head;
	private DNode tail;

	public void add(E toAdd){
		DNode newNode = new DNode();
		newNode.element = toAdd;
		if(size > 1) {
			this.tail.next = newNode;
			newNode.prev = this.tail;
			this.tail = newNode;
		}
		else if(size == 0){
			this.head = newNode;
			this.tail = newNode;
		}
		else {
			newNode.prev = this.head;
			this.tail = newNode;
			this.head.next = newNode;
		}
		this.size += 1;
	}
	public E remove(){
		if(this.size == 0){
			throw new NoSuchElementException("List is empty");
		}
		if(this.size == 1){
			E elem = this.head.element;
			this.clear();
			return elem;
		}
		DNode newTail = this.tail.prev;
		DNode oldTail = this.tail;
		newTail.next = null;
		this.tail = newTail;
		this.size -= 1;
		return oldTail.element;
	}
	public void clear(){
		this.head = null;
		this.tail= null;
		this.size = 0;
	}
	public void addFirst(E toAdd) {
		if(this.size == 0){
			this.add(toAdd);
			return;
		}
		DNode newNode = new DNode();
		newNode.element = toAdd;
		this.head.prev = newNode;
		newNode.next = this.head;
		this.head = newNode;
		this.size += 1;
	}
	public void addLast(E toAdd){
		this.add(toAdd);
	}
	public E removeFirst(){
		if(this.size == 0){
			throw new NoSuchElementException("List is empty");
		}
		if(this.size == 1){
			E elem = this.head.element;
			this.clear();
			return elem;
		}
		E placeholder = this.head.element;
		this.head = this.head.next;
		this.head.prev = null;
		size -= 1;
		return placeholder;
	}
	public E removeLast(){
		return this.remove();
	}
	public E peekFirst(){
		if(this.size == 0){
			throw new NoSuchElementException("List is empty");
		}
		return this.head.element;
	}
	public E peekLast(){
		if(this.size == 0){
			throw new NoSuchElementException("List is empty");
		}
		return this.tail.element;
	}
	public boolean equals(Object toCompare){
		if(toCompare instanceof Caterpillar){
			if(!(this instanceof Caterpillar)){
				return false;
			}
			Iterator<Position> aIter = ((Caterpillar) toCompare).iterator();
			Iterator<Position> bIter = ((Caterpillar) this).iterator();
			Position a;
			Position b;
			while (aIter.hasNext()){
				a = aIter.next();
				b = bIter.next();
				if(!a.equals(b)){
					return false;
				}
			}
			return true;

		} else if(!(toCompare instanceof MyDoublyLinkedList)){
			return false;
		}
		MyDoublyLinkedList<E> aList = (MyDoublyLinkedList<E>) toCompare;
		if(this.getSize() == 0 && aList.getSize() == 0){
			return true;
		} else if(this.getSize() != aList.getSize()){
			return false;
		}
		Iterator<E> aIter = aList.iterator();
		Iterator<E> bIter = this.iterator();
		Object a;
		Object b;
		while(bIter.hasNext()){
			a = aIter.next();
			b = bIter.next();
			if(a != b){
				return false;
			}
		}
		return true;
	}

	public Iterator<E> iterator() {
		return new DLLIterator();
	}

	private class DNode {
		private E element;
		private DNode next;
		private DNode prev;
	}

	private class DLLIterator implements Iterator<E> {
		DNode curr;

		public DLLIterator() {
			this.curr = head;
		}

		public boolean hasNext() {
			return this.curr != null;
		}

		public E next() {
			if (!this.hasNext())
				throw new NoSuchElementException();

			E element = this.curr.element;
			this.curr = this.curr.next;
			return element;
		}
	}
}
