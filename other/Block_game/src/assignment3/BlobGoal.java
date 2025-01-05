package assignment3;

import java.awt.Color;

public class BlobGoal extends Goal{

	public BlobGoal(Color c) {
		super(c);
	}

	@Override
	public int score(Block board) {
		Color[][] colorBoard = board.flatten();
		int boardSize = colorBoard[0].length;
		int maxScore = 0;
		int scoreCompare = 0;
		boolean[][] visited = new boolean[boardSize][boardSize];
		for(int i = 0; i < boardSize; i++){
			for(int j = 0; j < boardSize; j++){
				scoreCompare = undiscoveredBlobSize(i,j,colorBoard,visited);

				if(scoreCompare>maxScore) maxScore = scoreCompare;
			}
		}
		return maxScore;
	}

	@Override
	public String description() {
		return "Create the largest connected blob of " + GameColors.colorToString(targetGoal) 
		+ " blocks, anywhere within the block";
	}


	public int undiscoveredBlobSize(int i, int j, Color[][] unitCells, boolean[][] visited) {
		if(unitCells[i][j] != this.targetGoal) {
			return 0;
		}
		int blobSize = 1;
		visited[i][j] = true;
		if(j < visited.length - 1) {
			if (!visited[i][j + 1]) {
				blobSize += undiscoveredBlobSize(i, j + 1, unitCells, visited);
			}
		}
		if(j>1){
			if(!visited[i][j-1]){
				blobSize += undiscoveredBlobSize(i,j-1,unitCells, visited);
			}
		}
		if(i < visited.length - 1) {
			if (!visited[i + 1][j]) {
				blobSize += undiscoveredBlobSize(i + 1, j, unitCells, visited);
			}
		}
		if(i>1) {
			if (!visited[i - 1][j]) {
				blobSize += undiscoveredBlobSize(i - 1, j, unitCells, visited);
			}
		}
		return blobSize;
	}

}
