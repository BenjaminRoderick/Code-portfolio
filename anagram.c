//Benjamin Roderick
//This short program takes as input a string, and determines if it's an anagram

#include <stdio.h>
#include <string.h>

int main (int argc, char *argv[])
{
	char a[30];
	strcpy(a, argv[1]);
	char b[30];
	strcpy(b, argv[2]);
	int aLength = strlen(a);
	int bLength = strlen(b);
	int i;
	int j;

	if(aLength != bLength)//if the two words have do not have the same length, they can not be anagrams.
	{
		printf("Not an anagram");
		return 1;
	}

	for(i = 0; i < aLength; i++)
	{
		for(j = 0; j < bLength; j++)
		{
			if(a[i] == b[j])
			{
				b[j] = '\0';//replace all hits with null characters.
				break;
			}
		}
	}

	for(i = 0; i < bLength; i++)
	{
		if(b[i] != '\0')
		{
			printf("Not an anagram");
			return 1;
		}
	}

	printf("Anagram");
	return 0;
}
