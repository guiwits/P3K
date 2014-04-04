import java.io.*;
import java.net.*;
import java.awt.*;

public class GenIIISend {
	
	public static void main (String [] args) {

		String host = "192.168.0.100";
		int driverNumber = 0;
		int port = 0;
		Socket s = null;
		BufferedReader input = null;
		DataOutputStream output = null;

		/* GenIII variables */
		String response = null;
		String reply = null;
		String cmd = null;
		String clear = "0";
		String pwrOn = "1";
		String ack = ">";
		String nack = "?";
		
		if (args.length < 3) {
			System.out.println ("Usage: java GenIIISend <host> <driver number> <cmd>");
			System.exit (1);
		}
		
		try {
			host = args[0];
			driverNumber = Integer.parseInt (args[1]);
			cmd = args[2];
		} catch (Exception e) {
			System.out.println ("Error: Arguments format is wrong.");
			System.exit (1);
		}
		
		if (driverNumber == 0) {
			port = 10000;
		} else if (driverNumber == 1) {
			port = 10001;
		} else if (driverNumber == 2) {
			port = 10002;
		} else if (driverNumber == 3) {
			port = 10003;
		} else if (driverNumber == 4) {
			port = 10004;
		} else if (driverNumber == 5) {
			port = 10005;
		} else if (driverNumber == 6) {
			port = 10006;
		} else if (driverNumber == 7) {
				port = 10007;
		} else {
			System.out.println ("ERROR: Driver Number must be between 0 and 7");
			System.exit (-1);
		}
		
		System.out.println ("DEBUG: port = " + port);
		
		try {
			s = new Socket (host, port);
		} catch (IOException e) {
			System.out.println ("Cannot resolve hostname or address.");
			System.exit (-1);
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

		
		/* Send/recieve data to/from the GenIII DM Driver */
		try {
			/*####### Send command to clear driver sequence ######*/
			output.writeBytes (clear);
			output.flush ();

			/* Check to see if a successful acknowledgement was received*/
			while ((response = input.readLine()) != null) {
			    if (response.indexOf (ack) != -1) { 
				break;
			    }
			}
			/*##########################################################*/

			try { 
				Thread.sleep (1000); 
			} catch (Exception e) { 
				System.out.println (e); 
			}
			
			output.writeBytes (cmd);
			output.flush();
			
			/* Check to see if a successful acknowledgement was received*/
			while ((response = input.readLine()) != null) {
			    if (response.indexOf (ack) != -1) { 
					break;
			    }
			}
			/*##########################################################*/
			

			/*######### Send poweron sequence ##########*/
			output.writeBytes (pwrOn);
			output.flush();
			while ((response = input.readLine()) != null) {
				if (response.indexOf (ack) != -1) { 
					break;
				} else if (response.indexOf (nack) != -1) {
					System.out.println ("ERROR: Failed bringing up the driver.\n");
				}
			} 
			/*##########################################*/

		} catch (IOException e) {
			System.out.println ("Error sending/receiving data.");
		}
		
		/* Close all connections and streams */
		try {
			input.close();
			output.close();
			s.close();

		} catch (IOException e) {
			System.out.println (e);
			System.exit (1);
		}
		
		System.out.println ("\r\rGenIII Driver command successfully sent.\r");
		System.exit (0);
	}
}
