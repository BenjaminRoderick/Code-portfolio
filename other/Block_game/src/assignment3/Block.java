package assignment3;

import java.util.ArrayList;
import java.util.Random;
import java.awt.Color;

public class Block {
    private int xCoord;
    private int yCoord;
    private int size; // height/width of the square
    private int level; // the root (outer most block) is at level 0
    private int maxDepth;
    private Color color;//should be null if not a leaf

    private Block[] children; // {UR, UL, LL, LR}

    public static Random gen = new Random();


    /*
     * These two constructors are here for testing purposes.
     */
    public Block() {}

    public Block(int x, int y, int size, int lvl, int  maxD, Color c, Block[] subBlocks) {
        this.xCoord=x;
        this.yCoord=y;
        this.size=size;
        this.level=lvl;
        this.maxDepth = maxD;
        this.color=c;
        this.children = subBlocks;
    }



    /*
     * Creates a random block given its level and a max depth.
     *
     * xCoord, yCoord, size, and highlighted should not be initialized
     * (i.e. they will all be initialized by default)
     */
    public Block(int lvl, int maxDepth) {
        this.level = lvl;
        this.maxDepth = maxDepth;
        if(lvl>maxDepth) throw new IllegalArgumentException("level cannot be bigger than max depth");

        boolean subdivided = false;

        if(lvl < maxDepth){
            double randNum = gen.nextDouble();
            this.children = new Block[4];

            if(randNum < Math.exp(-0.25*level)){
                subdivided = true;
                for(int i = 0; i < 4; i++){
                    this.children[i] = new Block(lvl + 1, maxDepth);
                }
            }
        }
        if(!subdivided){
            this.children = new Block[0];
            int randInt = gen.nextInt(4);
            this.color = GameColors.BLOCK_COLORS[randInt];
        }
    }


    /*
     * Updates size and position for the block and all of its sub-blocks, while
     * ensuring consistency between the attributes and the relationship of the
     * blocks.
     *
     *  The size is the height and width of the block. (xCoord, yCoord) are the
     *  coordinates of the top left corner of the block.
     */
    public void updateSizeAndPosition (int size, int xCoord, int yCoord) {
        if(size < 1){
            throw new IllegalArgumentException("Invalid size");
        }

        int modulo = size;
        boolean good = true;
        while (good){
            if(modulo == 2 || modulo == 1){
                break;
            }
            if(modulo%2 != 0){
                good = false;
            } else {
                modulo /= 2;
            }
        }

        if(!good)throw new IllegalArgumentException("Invalid size");

        this.size = size;
        this.xCoord = xCoord;
        this.yCoord = yCoord;

        if(this.level < maxDepth && this.children.length == 4) {
            int halfSize = size / 2;
            this.children[0].updateSizeAndPosition(halfSize, xCoord + halfSize, yCoord);
            this.children[1].updateSizeAndPosition(halfSize, xCoord, yCoord);
            this.children[2].updateSizeAndPosition(halfSize, xCoord, yCoord + halfSize);
            this.children[3].updateSizeAndPosition(halfSize, xCoord + halfSize, yCoord + halfSize);
        }
    }


    /*
     * Returns a List of blocks to be drawn to get a graphical representation of this block.
     *
     * This includes, for each undivided Block:
     * - one BlockToDraw in the color of the block
     * - another one in the FRAME_COLOR and stroke thickness 3
     *
     * Note that a stroke thickness equal to 0 indicates that the block should be filled with its color.
     *
     * The order in which the blocks to draw appear in the list does NOT matter.
     */
    public ArrayList<BlockToDraw> getBlocksToDraw() {
        ArrayList<BlockToDraw> blockList = new ArrayList<BlockToDraw>();

        if(this.children.length == 0){
            blockList.add(new BlockToDraw(this.color, this.xCoord, this.yCoord, this.size, 0));
            blockList.add(new BlockToDraw(GameColors.FRAME_COLOR, this.xCoord, this.yCoord, this.size, 3));
        } else {
            for (int i = 0; i < 4; i++){
                blockList.addAll(this.children[i].getBlocksToDraw());
            }
        }
        return blockList;
    }

    /*
     * This method is provided and you should NOT modify it.
     */
    public BlockToDraw getHighlightedFrame() {
        return new BlockToDraw(GameColors.HIGHLIGHT_COLOR, this.xCoord, this.yCoord, this.size, 5);
    }



    /*
     * Return the Block within this Block that includes the given location
     * and is at the given level. If the level specified is lower than
     * the lowest block at the specified location, then return the block
     * at the location with the closest level value.
     *
     * The location is specified by its (x, y) coordinates. The lvl indicates
     * the level of the desired Block. Note that if a Block includes the location
     * (x, y), and that Block is subdivided, then one of its sub-Blocks will
     * contain the location (x, y) too. This is why we need lvl to identify
     * which Block should be returned.
     *
     * Input validation:
     * - this.level <= lvl <= maxDepth (if not throw exception)
     * - if (x,y) is not within this Block, return null.
     */
    public Block getSelectedBlock(int x, int y, int lvl) {
        if(this.level > lvl){
            throw new IllegalArgumentException("Level smaller than block's level");
        }
        if(this.maxDepth < lvl){
            throw new IllegalArgumentException("Level larger than max depth");
        }
        if(x < this.xCoord || y < this.yCoord || x > this.xCoord+this.size || y > this.yCoord+this.size) {
            return null;
        }
        if(lvl == this.level){
            return this;
        }
        return this.traversalSearch(x,y,lvl);
    }

    private Block traversalSearch(int x, int y, int lvl){
        if(this.children.length == 0 || this.level == lvl){
            if(x >= this.xCoord && y >= this.yCoord && x < this.xCoord+this.size && y < this.yCoord+this.size) {
                return this;
            }
            return null;
        }
        Block temp = null;
        for(Block a: this.children){
            temp = a.traversalSearch(x,y,lvl);

            if(temp != null){
                break;
            }
        }
        return temp;
    }



    /*
     * Swaps the child Blocks of this Block.
     * If input is 1, swap vertically. If 0, swap horizontally.
     * If this Block has no children, do nothing. The swap
     * should be propagate, effectively implementing a reflection
     * over the x-axis or over the y-axis.
     *
     */
    public void reflect(int direction) {
        if(direction != 0 && direction != 1){
            throw new IllegalArgumentException("Incorrect direction parameter");
        }
        if(direction == 0){
            this.xReflect();
        }
        else {
            this.yReflect();
        }
    }

    private void xReflect(){
        if(this.children.length == 4){
            Color temp = this.children[1].color;
            this.children[1].color = this.children[2].color;
            this.children[2].color = temp;
            temp = this.children[0].color;
            this.children[0].color = this.children[3].color;
            this.children[3].color = temp;
            for(Block a: this.children){
                a.xReflect();
            }
        }
    }

    private void yReflect(){
        if(this.children.length == 4){
            Color temp = this.children[1].color;
            this.children[1].color = this.children[0].color;
            this.children[0].color = temp;
            temp = this.children[2].color;
            this.children[2].color = this.children[3].color;
            this.children[3].color = temp;
            for(Block a: this.children){
                a.yReflect();
            }
        }
    }

    /*
     * Rotate this Block and all its descendants.
     * If the input is 1, rotate clockwise. If 0, rotate
     * counterclockwise. If this Block has no children, do nothing.
     */
    public void rotate(int direction) {
        if(direction != 0 && direction != 1){
            throw new IllegalArgumentException("Invalid direction");
        }
        if(direction == 0){
            this.reflect(1);
            this.diagonalReflect();
        } else{
            this.reflect(0);
            this.diagonalReflect();
        }
    }
    private void diagonalReflect(){
        int temp = this.xCoord;
        this.xCoord = this.yCoord;
        this.yCoord = temp;

        if(this.children.length == 4){
            for(Block a: this.children){
                a.diagonalReflect();
            }
        }
    }



    /*
     * Smash this Block.
     *
     * If this Block can be smashed,
     * randomly generate four new children Blocks for it.
     * (If it already had children Blocks, discard them.)
     * Ensure that the invariants of the Blocks remain satisfied.
     *
     * A Block can be smashed iff it is not the top-level Block
     * and it is not already at the level of the maximum depth.
     *
     * Return True if this Block was smashed and False otherwise.
     *
     */
    public boolean smash() {
        if(this.level >= this.maxDepth || this.level == 0){
            return false;
        }
        for(int i = 0; i < 4; i++){
            this.children[i] = new Block(this.level+1, this.maxDepth);
        }
        this.updateSizeAndPosition(this.size, this.xCoord, this.yCoord);
        return true;
    }


    /*
     * Return a two-dimensional array representing this Block as rows and columns of unit cells.
     *
     * Return and array arr where, arr[i] represents the unit cells in row i,
     * arr[i][j] is the color of unit cell in row i and column j.
     *
     * arr[0][0] is the color of the unit cell in the upper left corner of this Block.
     */
    public Color[][] flatten() {
        Color[][] gameArray = this.treeToArray();

        return gameArray;
    }
    private Color[][] treeToArray(){
        int arrSize = (int) Math.pow(2, this.maxDepth - this.level);

        Color[][] colorArray = new Color[arrSize][arrSize];
        if(this.color != null){
            for(int i = 0; i < arrSize; i++){
                for(int j = 0; j < arrSize; j++){
                    colorArray[i][j] = this.color;
                }
            }
            return colorArray;
        } else if(arrSize == 2){
            colorArray[0][0] = this.children[1].color;
            colorArray[0][1] = this.children[0].color;
            colorArray[1][0] = this.children[2].color;
            colorArray[1][1] = this.children[3].color;
            return colorArray;
        }
        Color[][] a = this.children[0].treeToArray();
        Color[][] b = this.children[1].treeToArray();
        Color[][] c = this.children[2].treeToArray();
        Color[][] d = this.children[3].treeToArray();
        int halfSize = arrSize/2;
        for(int i = 0; i < arrSize; i++){
            for(int j = 0; j < arrSize; j++){
                if(i<halfSize && j<halfSize){
                    colorArray[i][j] = b[i][j];
                } else if(i>=halfSize && j<halfSize){
                    colorArray[i][j] = c[i-halfSize][j];
                } else if(i<halfSize && j>=halfSize){
                    colorArray[i][j] = a[i][j-halfSize];
                } else {
                    colorArray[i][j] = d[i-halfSize][j-halfSize];
                }
            }
        }
        return colorArray;
    }

    // These two get methods have been provided. Do NOT modify them.
    public int getMaxDepth() {
        return this.maxDepth;
    }

    public int getLevel() {
        return this.level;
    }


    /*
     * The next 5 methods are needed to get a text representation of a block.
     * You can use them for debugging. You can modify these methods if you wish.
     */
    public String toString() {
        return String.format("pos=(%d,%d), size=%d, level=%d"
                , this.xCoord, this.yCoord, this.size, this.level);
    }

    public void printBlock() {
        this.printBlockIndented(0);
    }

    private void printBlockIndented(int indentation) {
        String indent = "";
        for (int i=0; i<indentation; i++) {
            indent += "\t";
        }

        if (this.children.length == 0) {
            // it's a leaf. Print the color!
            String colorInfo = GameColors.colorToString(this.color) + ", ";
            System.out.println(indent + colorInfo + this);
        } else {
            System.out.println(indent + this);
            for (Block b : this.children)
                b.printBlockIndented(indentation + 1);
        }
    }

    private static void coloredPrint(String message, Color color) {
        System.out.print(GameColors.colorToANSIColor(color));
        System.out.print(message);
        System.out.print(GameColors.colorToANSIColor(Color.WHITE));
    }

    public void printColoredBlock(){
        Color[][] colorArray = this.flatten();
        for (Color[] colors : colorArray) {
            for (Color value : colors) {
                String colorName = GameColors.colorToString(value).toUpperCase();
                if(colorName.length() == 0){
                    colorName = "\u2588";
                }else{
                    colorName = colorName.substring(0, 1);
                }
                coloredPrint(colorName, value);
            }
            System.out.println();
        }
    }

}
