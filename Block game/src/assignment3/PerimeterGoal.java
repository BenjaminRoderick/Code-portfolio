package assignment3;

import java.awt.Color;

public class PerimeterGoal extends Goal{

	public PerimeterGoal(Color c) {
		super(c);
	}

	@Override
	public int score(Block board) {
		Color[][] boardMatrix = board.flatten();
		int sum = 0;
		int sideLength = boardMatrix[0].length;
		//top row
		for(int i = 0; i<sideLength; i++){
			if(boardMatrix[0][i] == this.targetGoal){
				sum++;
			}
		}
		//bottom row
		for(int i = 0; i<sideLength; i++){
			if(boardMatrix[sideLength-1][i] == this.targetGoal){
				sum++;
			}
		}
		//left column
		for(int i = 0; i<sideLength; i++){
			if(boardMatrix[i][0] == this.targetGoal){
				sum++;
			}
		}
		//right column
		for(int i = 0; i<sideLength; i++){
			if(boardMatrix[i][sideLength-1] == this.targetGoal){
				sum++;
			}
		}
		return sum;
	}

	@Override
	public String description() {
		return "Place the highest number of " + GameColors.colorToString(targetGoal) 
		+ " unit cells along the outer perimeter of the board. Corner cell count twice toward the final score!";
	}

}
