import java.sql.* ;
import java.util.HashMap;
import java.util.Locale;
import java.util.Scanner;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDate;
import java.sql.Date;
class simpleJDBC
{
    public static void main ( String [ ] args ) throws SQLException
    {
      // Unique table names.  Either the user supplies a unique identifier as a command line argument, or the program makes one up.
        String tableName;
        int sqlCode;      // Variable to hold SQLCODE
        String sqlState;  // Variable to hold SQLSTATE

//        if ( args.length > 0 )
//            tableName += args [ 0 ] ;
//        else
//          tableName += "exampletbl";

        // Register the driver.  You must register the driver before you can use it.
        try { DriverManager.registerDriver ( new com.ibm.db2.jcc.DB2Driver() ) ; }
        catch (Exception cnfe){ System.out.println("Class not found"); }
        String passwd = "";
        try {
            BufferedReader reader = new BufferedReader(new FileReader("info.txt"));
            passwd = reader.readLine();
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        // TODO HERE: Fill in your database URL, user id and password below.
        // NOTE: you will need to set up your own database server
        String url = "YOUR_URL_HERE";

        String your_userid = "ID_HERE";
        String your_password = passwd;
        //AS AN ALTERNATIVE, you can just set your password in the shell environment in the Unix (as shown below) and read it from there.
        //$  export PASSWORD=yoursocspasswd 
        if(your_userid == null && (your_userid = System.getenv("USER")) == null)
        {
          System.err.println("Error!! do not have a password to connect to the database!");
          System.exit(1);
        }
        if(your_password == null && (your_password = System.getenv("PASSWORD")) == null)
        {
          System.err.println("Error!! do not have a password to connect to the database!");
          System.exit(1);
        }
        Connection con = DriverManager.getConnection (url,your_userid,your_password) ;
        Statement statement = con.createStatement () ;
//        DatabaseMetaData metaData = con.getMetaData();
//        ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});
//
//        System.out.println("Tables in the current database:");
//        while (tables.next()) {
//            System.out.println(tables.getString("TABLE_NAME"));
//        }
//
//        tables.close();
        Scanner scanner = new Scanner(System.in);
        System.out.println("Connected to the database.");
        boolean running = true;

        while (running) {
            System.out.println("\nMenu:");
            System.out.println("1. View a Tutors services");
            System.out.println("2. Search for services by subject and education level");
            System.out.println("3. Delete a user post");
            System.out.println("4. Purchase a service");
            System.out.println("5. View who liked a post");
            System.out.println("6. Quit");
            System.out.print("Select an option: ");

            int choice = scanner.nextInt();
            scanner.nextLine(); // Consume newline
            String querySQL = "";
            java.sql.ResultSet rs;
            PreparedStatement preparedStatement;
            try {
                switch (choice) {
                    case 1:
                        System.out.println("You selected option 1");
                        System.out.println("Input a Tutor email:");
                        String email = scanner.nextLine();
                        querySQL = "SELECT name, subject, price, edu_level from Service s WHERE s.email = ?";
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, email);
                        //System.out.println(querySQL);
                        rs = preparedStatement.executeQuery();
                        if (!rs.next()){
                            System.out.println("Sorry there are no tutors under that email!");
                            break;
                        }
                        do {
                            String res_name = rs.getString ( "name") ;
                            //String name = rs.getString (2);
                            System.out.println ("name:  " + res_name);
                            //System.out.println ("name:  " + name);
                        } while (rs.next());
                        break;
                    case 2:
                        System.out.println("You selected option 2");
                        System.out.println("What subject are you studying?");
                        String subj = scanner.nextLine();
                        System.out.println("What is the desired education level?");
                        String edu_lvl = scanner.nextLine();
                        querySQL = "SELECT email, name, subject, price, edu_level from " + "Service " + "WHERE subject = ? AND edu_level = ?";
                        //System.out.println(querySQL);
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, subj);
                        preparedStatement.setString(2, edu_lvl);
                        rs = preparedStatement.executeQuery();
                        if (!rs.next()){
                            System.out.println("Sorry there are no services for that subject and education level!");
                            break;
                        }
                        do {
                            String res_email = rs.getString ( "email") ;
                            //String name = rs.getString (2);
                            System.out.println ("Tutor: "+rs.getString("email") +" "+  "Title: "+ rs.getString("name") +" "+ "Price: "+rs.getString("price")+"$");
                            //System.out.println ("name:  " + name);
                        } while ( rs.next ( ) );
                        break;
                    case 3:
                        System.out.println("You selected option 3");
                        System.out.println("Input the email of the user who made the post:");
                        String email_3 = scanner.nextLine();
                        querySQL = "SELECT * from Post WHERE email = ?";
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, email_3);
                        rs = preparedStatement.executeQuery();
                        if (!rs.next()){
                            System.out.println("That user has no posts sorry!");
                            break;
                        }
                        else {
                            HashMap post_map = new HashMap<Integer, Integer>();
                            int counter = 0;

                            if(!rs.next()){
                                System.out.println("sorry we cannot find any posts by that user");
                                break;
                            }
                            System.out.println("Below are the posts made by that user, please select the one you wish to delete");
                            do  {
                                counter++;
                                post_map.put(counter, rs.getInt("pID"));
                                //String name = rs.getString (2);
                                System.out.println(counter + ".  pid: " + rs.getInt("pID") + " title:" + rs.getString("Title"));
                                //System.out.println ("name:  " + name);
                            } while (rs.next());
                            boolean running2 = true;
                            System.out.println("To select the post please input the index of the post displayed on screen, to abort enter -1");
                            while (running2) {
                                int choice2 = scanner.nextInt();
                                scanner.nextLine();
                                if (post_map.containsKey(choice2)) {
                                    querySQL = "DELETE FROM Post WHERE pID = ?";
                                    preparedStatement = con.prepareStatement(querySQL);
                                    preparedStatement.setString(1, (post_map.get(choice2)).toString());
                                    preparedStatement.executeUpdate();
                                    running2 = false;
                                } else if (choice2 == -1) {
                                    running2 = false;
                                } else {
                                    System.out.println("Invalid choice please try again");
                                }
                            }
                        }
                        break;
                    case 4:
                        System.out.println("You selected option 4");
                        System.out.println("Input the email of the Tutor who offers the service:");
                        String email_4 = scanner.nextLine();
                        System.out.println("Input the name of the service:");
                        String name_4 = scanner.nextLine();
                        querySQL = "SELECT Count(*) FROM Purchase p WHERE p.email_seller = ? AND p.name = ?";
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, email_4);
                        preparedStatement.setString(2, name_4);
                        //System.out.println(preparedStatement.toString());
                        rs = preparedStatement.executeQuery();
                        int num_participants = 0;
                        while (rs.next()) {
                            num_participants = rs.getInt(1);
                            System.out.println("The number of people who have purchased this service: "+rs.getInt(1));
                            //System.out.println ("name:  " + name);
                        }
                        //int num_participants = 0;
                        //System.out.println(num_participants);
                        querySQL = "SELECT * FROM Tutorial_session WHERE email = ? AND name = ?";
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, email_4);
                        preparedStatement.setString(2, name_4);
                        //System.out.println(preparedStatement);

                        rs = preparedStatement.executeQuery();
                        if (!rs.next() || rs.getInt("max_participants") > num_participants){
                            System.out.println("The service is available for purchase, Enter y to continue, n to abort");
                            String continuation = scanner.nextLine();
                            switch (continuation){
                                case "y":
                                    System.out.println("Please input your user email");
                                    String user_email = scanner.nextLine();
                                    querySQL = "INSERT INTO Purchase VALUES (?, ?, ?, ?)";
                                    preparedStatement = con.prepareStatement(querySQL);
                                    preparedStatement.setString(1, user_email);
                                    preparedStatement.setString(2, email_4);
                                    preparedStatement.setString(3, name_4);
                                    preparedStatement.setDate(4, Date.valueOf(LocalDate.now()));
                                    preparedStatement.executeUpdate();
                                    break;
                                case "n":
                                    System.out.println("aborting purchase");
                            }
                        }
                        else{
                            System.out.println("Unfortunately this service is full");
                        }
                        break;
                    case 5:
                        System.out.println("You selected option 5");
                        System.out.println("Please input the pID of the post:");
                        String pID = scanner.nextLine();
                        querySQL = "SELECT * FROM post_like WHERE pID = ?";
                        preparedStatement = con.prepareStatement(querySQL);
                        preparedStatement.setString(1, pID);
                        rs = preparedStatement.executeQuery();
                        if (!rs.next()){
                            System.out.println("Sorry, we cannot find any likes on a post with that ID");
                            break;
                        }
                        do {
                            System.out.println(rs.getString("email"));
                            //System.out.println ("name:  " + name);
                        } while (rs.next());
                        break;
                    case 6:
                        System.out.println("Exiting program.");
                        running = false;
                        break;
                    default:
                        System.out.println("Invalid option. Please try again.");
                }
            }
            catch (SQLException e){
                sqlCode = e.getErrorCode(); // Get SQLCODE
                sqlState = e.getSQLState(); // Get SQLSTATE
                System.out.println("Code: " + sqlCode + "  sqlState: " + sqlState);
                System.out.println(e);
            }
        }
        statement.close ( ) ;
        con.close ( ) ;
    }
}
