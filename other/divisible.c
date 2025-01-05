//Benjamin Roderick
//takes as input 3 numbers, determines if they are increasing and if the first divides the rest

#include <stdio.h>

int main (void)
{
	printf("Please input 3 numbers: ");

	int a;
	int b;
	int c;
	
	scanf("%d %d %d", &a, &b, &c);//assign values to the variables.

	if(a<b && b<c)//check if increasing.
	{
		if(a == 0)//zero division edge case.
		{
			printf("Not divisible & Increasing");
			return 1;
		}

		if((b%a == 0) && (c%a == 0))//divisible condition.
		{
			printf("Divisible & Increasing");
			return 0;
		}
		else
		{
			printf("Not divisible & Increasing");
			return 1;
		}
	}
	else
	{
		if(a == 0)
		{
			printf("Not divisible & Not increasing");
			return 3;
		}

		if((b%a == 0) && (c%a == 0))
		{
 			printf("Divisible & Not increasing");
 			return 2;
 		}
 		else
		{
 			printf("Not divisible & Not increasing");
 			return 3;
 		}
	}
}
