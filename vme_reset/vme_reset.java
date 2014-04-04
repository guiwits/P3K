import java.io.*;
import java.net.*;
import java.awt.*;

public class vme_reset {
	
	public static void main (String [] args) {

		String host = null;
		int port = 3001;
		Socket s = null;
		BufferedReader input = null;
		DataOutputStream output = null;

		/* Pulizzi variables */
		String ipc = "IPC ONLINE!";
		String initialize = "@@@@\r";
		String shutdown = "A00\r";
		String poweron = "S10\r";
		String response = null;
		String reply = "DONE";
		
		if (args.length != 2) {
			System.out.println ("Usage: java vme_reset <host> <port>");
			System.exit (1);
		}
		
		try {
			host = args[0];
			port = Integer.parseInt (args[1]);
		} catch (Exception e) {
			System.out.println ("Error: Arguments format is wrong.");
			System.exit (1);
		}
		
		try {
			s = new Socket (host, port);
		} catch (IOException e) {
			System.out.println ("Cannot resolve hostname or address.");
			System.exit (1);
		}

		/* Initialize Data Input Stream */
		try {
		    input = new BufferedReader (new InputStreamReader (s.getInputStream()));
		} catch (IOException e) {
		    System.out.println (e);
		}

		/* Initialize Data Output Stream */
		try {
		    output = new DataOutputStream (s.getOutputStream());
		} catch (IOException e) {
		    System.out.println (e);
		}

		
		/* Send/recieve data to/from pulizzi */
		try {
			/*######### Send initialization sequence #########*/
			output.writeBytes (initialize);
			output.flush ();

			/* Check to see if a successful init string was sent */
			while ((response = input.readLine()) != null) {
			    if (response.indexOf (ipc) != -1) { 
				break;
			    }
			}
			/*################################################*/

			try { 
				Thread.sleep (1250); 
			} catch (Exception e) { 
				System.out.println (e); 
			}


			/*######### Send poweroff sequence #########*/
			output.writeBytes (shutdown);
			output.flush();

			while ((response = input.readLine()) != null) {
                            if (response.indexOf (reply) != -1) { 
                                break;
                           }
                       }
			/*##########################################*/

		       try { 
			   Thread.sleep (1250);
		       } catch (Exception e) {
			   System.out.println (e);
		       }

			/*######### Send poweron sequence ##########*/
		       output.writeBytes (poweron);
		       output.flush();
		       while ((response = input.readLine()) != null) {
			   if (response.indexOf (reply) != -1) { 
			       break;
			   }
		       } 
			/*##########################################*/

		} catch (IOException e) {
			System.out.println ("Error sending/receiving data.");
		}


		{ /* internal block */
		System.out.print ("Please wait while vme_reset resets ");
		int countdown = 0;
		while (countdown != 9) {
			System.out.print (". ");
			try {
				Thread.sleep (1000);
			} catch (Exception e) {
				System.out.println (e);
			} 
			countdown = countdown + 1;
		}
		} /* End internal block */
		
		/* Close all connections and streams */
		try {
			input.close();
			output.close();
			s.close();

		} catch (IOException e) {
			System.out.println (e);
			System.exit (1);
		}
		
		System.out.println ("\r\r\rvme_reset complete.                                    \r");
		System.exit (0);
	}
}
