package assignment2;

public class Main {
    public static void main(String[] args){
        Caterpillar caterpillar1 = new Caterpillar();
        System.out.println(caterpillar1.getClass());

        Caterpillar caterpillar2 = new Caterpillar();
        boolean compare = caterpillar2.getClass() == caterpillar1.getClass();
        System.out.println(compare);

        System.out.println(caterpillar1.equals(caterpillar2));
    }

}
