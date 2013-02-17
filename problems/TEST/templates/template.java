import java.io.*;
import java.util.*;

class template
{
	public static void main(String[] args) throws Exception
	{
		template t = new template();
		t.go();
	}

	public void go() throws Exception
	{
		Scanner s = new Scanner(System.in);
		int N = s.nextInt();

		int[] a = new int[N];
		for(int k=0; k<a.length; k++)
		{
			a[k] = s.nextInt();
		}
		int[] ans = positiveValues(a);
		printArray(ans);
	}

	public int[] positiveValues(int[] a)
	{
		// Your code goes here
	}

	public void printArray(int[] a)
	{
		for(int k=0; k<a.length; k++)
		{
			System.out.println(a[k]);
		}
	}
} 