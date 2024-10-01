//Simple calculator program in C# for working with n-th degree polynomials
//Can compute the value of f(x) for a given x or find one of the roots within a region given by the user

using System;
using System.Linq;

namespace Root_Finder
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Input order of the function:");
            

            int Forder = Convert.ToInt32(Console.ReadLine());
            //order of the function
            double[] Function = new double[Forder + 1];

            for (int i = 0; i < Function.Length; i++)
            {
                Console.WriteLine("Order: " + i);
                Function[i] = Convert.ToDouble(Console.ReadLine());

            }
            //user assigns the coefficients of the function


            Console.Write("F(x)=");

            for (int i = Forder; i >= 0; i--)
            {
                Console.Write(Function[i]);
                Console.Write("x^" + i);

                if (i > 0)
                {
                    Console.Write("+");
                }

            }

            Console.WriteLine("");
            //prints the whole function

            Console.WriteLine("Operation?");
            Console.WriteLine("1: calculate F(x)");
            Console.WriteLine("2: find real roots");
            //what does the user want to do with the function

            int chooze = Convert.ToInt32(Console.ReadLine());
            switch (chooze) //actually does the operation
            {
                case 1: //calculate F(x)
                    Console.WriteLine("Assign a value to x");
                    double x = Convert.ToDouble(Console.ReadLine());

                    double yValue = Feval(Function, Forder, x);
                    Console.WriteLine(yValue);
                    break;

                case 2: //find root
                    double rootValue = Froot(Function, Forder);
                    Console.WriteLine("the x value is: " + rootValue);
                    break;

                default: //error message
                    Console.WriteLine("Invalid input");
                    break;
            }

        }

        static double Froot(double[] function, int forder)
        {
            //evaluate the roots of F(x)
            Console.WriteLine("Input 2 x values close to the root (use a graph)");
            Console.WriteLine("For each x, one must have a positive F(x), one negative and one \"guess\" that is close to the true root.");
            Console.WriteLine("1st guess (positive F(x))");

            double a = Convert.ToDouble(Console.ReadLine());
            double Fa = Feval(function, forder, a);

            Console.WriteLine("2nd guess (negative F(x))");

            double b = Convert.ToDouble(Console.ReadLine());
            double Fb = Feval(function, forder, b);

            double c = (a + b) / 2;
            double Fc = Feval(function, forder, c);
            //generate the first 3 guesses and their y values

            Console.WriteLine("F(a)=" + Fa);
            Console.WriteLine("F(b)=" + Fb);
            Console.WriteLine("F(c)=" + Fc);

            double d = c + (c - a) * (Math.Sign(Fa - Fb) * Fc) / (Math.Sqrt(Math.Pow(Fc, 2) - (Fa * Fb)));
            double Fd = Feval(function, forder, d);

            double epsilon = 0.0000000001;
            //setting the desired precision of the method

            while (Math.Abs(Fd) > epsilon)
            {
                if (Math.Sign(Fc) != Math.Sign(Fd))
                {
                    if (Math.Sign(Fd) == 1)
                    {
                        a = d;
                        Fa = Fd;
                        Fb = Fc;
                        c = (d + c) / 2;
                        Fc = Feval(function, forder, c);
                        //bracketed region becomes former Fd and Fc where Fd is positive
                    }
                    else
                    {
                        a = c;
                        Fa = Fc;
                        Fb = Fd;
                        c = (d + c) / 2;
                        Fc = Feval(function, forder, c);
                        //bracketed region becomes former Fd and Fc where Fc is positive
                    }

                }
                else
                {
                    if (Math.Sign(Fd) == -1)
                    {
                        Fb = Fd;
                        c = (d + a) / 2;
                        Fc = Feval(function, forder, c);                       
                        //bracketed region becomes former Fd and Fa where Fd is negative
                    }
                    else
                    {
                        a = d;
                        Fa = Fd;
                        c = (d + b) / 2;
                        Fc = Feval(function, forder, c);
                        //bracketed region becomes former Fd and Fb where Fd is positive
                    }

                }

                d = c + (c - a) * (Math.Sign(Fa - Fb) * Fc) / (Math.Sqrt(Math.Pow(Fc, 2) - (Fa * Fb)));
                Fd = Feval(function, forder, d);
                //computes values for next iteration
            }

            
            double root = d;

            return root;
            
        }

        static double Feval(double[] function, int forder, double xValue)
        {
            //function calc fast
            double[] Sfunction = new double[forder + 1];

            for (int i = forder; i >= 0; i--)
            {
                Sfunction[i] = function[i] * Math.Pow(xValue, i);

            }

            return Sfunction.Sum();


        }

    }

}