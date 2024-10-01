package assignment3;
import java.util.Random;
public class Main {
    public static void main(String[] args){
        Block.gen = new Random(2);
        Block test = new Block(0,2);
        test.updateSizeAndPosition(16,0,0);
        test.printColoredBlock();
    }
}
