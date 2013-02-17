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
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int T = Integer.parseInt(br.readLine());
		while(T-->0)
		{
			String line = br.readLine();
			String[] parts = line.split(" ");
			int N = parts.length;
			int[] tree = new int[N];
			for(int k=0; k<parts.length; k++)
			{
				String val = parts[k];
				tree[k] = Integer.parseInt(val);
			}

			boolean ans = isTree(tree);
			System.out.println(ans ? "YES" : "NO");
		}
	}

	public boolean isTree(int[] tree)
	{
		// Your code goes here
	}
} 