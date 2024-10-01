using System;
using System.Linq;
using System.Numerics;

namespace Root_Finder
{
    class Program
    {
        static void Main()
        {
            int Forder = -1;

            while (Math.Sign(Forder) == -1)
            {
                Console.WriteLine("Input order of function");
                //start text

                Forder = Convert.ToInt32(Console.ReadLine());
                //order of the function
            }
            double[] Function = new double[Forder + 1];

            for (int i = 0; i < Function.Length; i++)
            {
                Console.WriteLine("Order: " + i);
                Function[i] = Convert.ToDouble(Console.ReadLine());

            }
            //user assigns coefficients for each order of the function


            Console.Write("F(x)=");

            for (int i = Forder; i >= 0; i--)
            {
                if (i != Forder && Function[i] > 0)
                {
                    Console.Write("+");
                }

                if (Function[i] != 0)
                {
                    if (Function[i] != 1 || i == 0)
                    {
                        Console.Write(Function[i]);
                    }

                    if (i > 1)
                    {
                        Console.Write("x^" + i);
                    }
                    else if (i == 1)
                    {
                        Console.Write("x");
                    }
                }
               
            }

            Console.WriteLine("");
            //prints the whole function
            string answer = "placeholder";
            bool repeat = true;
            int chooze;
            while (repeat)
            {
                Console.WriteLine("Operation?");
                Console.WriteLine("1: calculate F(x)");
                Console.WriteLine("2: find real roots");
                Console.WriteLine("3: evaluate derivative");
                Console.WriteLine("4: calculate F(z) with complex input");
                Console.WriteLine("5: find all complex and real roots");
                //what does the user want to do with the function

                chooze = Convert.ToInt32(Console.ReadLine());
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
                    case 3: //derivative
                        double[] printDeriv = Fderive(Function, Forder);

                        Console.Write("F'(x)=");

                        for (int i = Forder - 1; i >= 0; i--)
                        {
                            if (i != Forder - 1 && printDeriv[i] > 0)
                            {
                                Console.Write("+");
                            }

                            if (printDeriv[i] != 0)
                            {
                                if (printDeriv[i] != 1 || i == 0)
                                {
                                    Console.Write(printDeriv[i]);
                                }

                                if (i > 1)
                                {
                                    Console.Write("x^" + i);
                                }
                                else if (i == 1)
                                {
                                    Console.Write("x");
                                }
                            }

                        }

                        Console.WriteLine("");
                        break;
                    case 4: //evaluate the polynomial with a complex input
                        Console.WriteLine("Input z value:");
                        Console.WriteLine("Input real component");
                        double real = Convert.ToDouble(Console.ReadLine());
                        Console.WriteLine("Input imaginary value (just the coefficient)");
                        double imaginary = Convert.ToDouble(Console.ReadLine());
                        Complex Zvalue = new Complex(real, imaginary);

                        Console.WriteLine(String.Format(new ComplexFormatter(), "{0:I0}", CFeval(Function, Forder, Zvalue)));
                        break;
                    case 5: //calculate all complex and real roots
                        Complex[] roots = new Complex[Forder];
                        roots = CFroot(Function, Forder);
                        for(int i = Forder - 1; i >= 0; i--)
                        {
                            //Console.WriteLine(String.Format(new ComplexFormatter(), "{0:I0}", roots[i]));
                            Console.WriteLine(roots[i]);
                        }                       
                        break;
                    default: //error message
                        Console.WriteLine("ERROR: invalid input, try again");
                        break;
                }
                while (answer != "y" && answer != "n")
                {
                    Console.WriteLine("Do you wish to do another operation?");
                    Console.WriteLine("y/n");
                    answer = Console.ReadLine();
                    if (answer == "n")
                    {
                        repeat = false;
                    }
                }
                answer = "placeholder";
            }

        }

        static double Froot(double[] function, int forder)
        {
            //evaluate the roots of F(x)
            double a;
            double b;
            double c;
            double d;

            if (forder == 0)
            {
                return double.NaN;//error message in case of evaluating the roots of a constant function
            }
            else if (forder == 1)
            {
                return function[0];//the root of a linear equation is the constant term
            }
            else if (forder == 2)
            {
                a = function[2];
                b = function[1];
                c = function[0];

                double discriminant = Math.Sqrt(Math.Pow(b, 2) - 4 * a * c);//the discriminant of a 2nd order polynomial is the portion of the quadratic formula that falls under the root

                Console.WriteLine("Discriminant of {0}", discriminant);
                Console.WriteLine("Add or subtract discriminant? (+/-)");
                string answer = Console.ReadLine();

                if (answer == "+")
                {
                    return (-1 * b + discriminant) / (2 * a);
                }
                else
                {
                    return (-1 * b - discriminant) / (2 * a);
                }

            }
            else if (forder >= 3)
            {
                Console.WriteLine("Input 2 x values close to the root");//the guesses are important because they greatly affect convergence speed
                Console.WriteLine("For each x, one must have a positive F(x) and one must have negative F(x).");
                Console.WriteLine("1st guess (positive F(x))");

                a = Convert.ToDouble(Console.ReadLine());
                double Fa = Feval(function, forder, a);

                Console.WriteLine("2nd guess (negative F(x))");

                b = Convert.ToDouble(Console.ReadLine());
                double Fb = Feval(function, forder, b);

                c = (a + b) / 2;//midpoint of the two guesses
                double Fc = Feval(function, forder, c);
                //generate the first 3 guesses and their y values

                Console.WriteLine("F(a)=" + Fa);
                Console.WriteLine("F(b)=" + Fb);
                Console.WriteLine("F(c)=" + Fc);

                d = c + (c - a) * (Math.Sign(Fa - Fb) * Fc) / Math.Sqrt(Math.Pow(Fc, 2) - (Fa * Fb));//using Ridder's method to compute the root of the polynomial
                double Fd = Feval(function, forder, d);

                double epsilon = 0.0000000001;
                //setting the desired precision of the method
                int iterations = 0;

                while (Math.Abs(Fd) > epsilon && iterations < 50)
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

                    iterations++; //iteration counter
                }

                if (iterations < 49)
                {
                    double root = d;
                    return root;
                }
            }

            return double.NaN;
        }

        static double Feval(double[] function, int forder, double xValue)//calculate F(x) for a given x
        {
            double Sfunction = 0;
            for (int i = forder; i >= 0; i--)
            {
                Sfunction += function[i];
                if(i != 0)
                {
                    Sfunction *= xValue;
                }
            }
            return Sfunction;
        }

        static double[] Fderive(double[] function, int forder)//take derivative of the polynomial
        {
            double[] derivative = new double[forder];
            for(int i = 0; i <= forder - 1; i++)
            {
                derivative[i] = function[i + 1] * (i + 1);
            }
            return derivative;
        }

        static Complex[] CFroot(double[] function, int forder)//complex number root finding using Durand-Kerner
        {
            double coeff = function[forder - 1];
            for(int i = 0; i < forder; i++)
            {
                function[i] /= coeff;
            }
            Complex[] roots = new Complex[forder];
            Complex[] rootsN = new Complex[forder];
            Complex[] divisor = new Complex[forder];
            double radius;
            if (function[0] != 0 && function[1] != 0)
            {
                radius = Math.Abs(forder * function[0] / (2 * function[1])) + Math.Abs(function[forder - 1] / (2 * forder * function[forder]));
            }
            else if(function[forder] != 0)
            {
                radius = Math.Pow(Math.Abs(function[0] / function[forder]), 1 / forder);
            }
            else
            {
                radius = Froot(function, forder);
            }
            if(radius == 0)
            {
                radius = Froot(function, forder);
            }
            if(radius == double.NaN)
            {
                radius = 1;
            }

            double argument = Math.PI / (2 * forder);

            for(int i = 0; i < forder; i++)//generate all the initial guesses along the perimiter of a ring
            {
                roots[i] = Complex.FromPolarCoordinates(radius, argument + 2 * Math.PI * i / forder);
            }

            int[] numOK = new int[forder];          
            bool cont = true;
            Complex denominator = new Complex(1, 0);
            double epsilon = 0.0000000001;
            int iterations = 0;

            while (cont)
            {
                for(int i = 0; i < forder; i++)
                {
                    for(int j = 0; j < forder; j++)
                    {
                        if(i != j)
                        {
                            divisor[j] = roots[i] - roots[j];
                        }
                        else
                        {
                            divisor[j] = Complex.One;
                        }
                    }
                    denominator = divisor.Aggregate((runningProduct, nextFactor) => runningProduct * nextFactor);
                    rootsN[i] = roots[i] - CFeval(function, forder, roots[i]) / denominator;//fixed point iteration to find the roots
                }
                for (int i = 0; i < forder; i++)//assign the new values
                {
                    if (rootsN[i].Real != double.NaN && rootsN[i].Imaginary != double.NaN)
                    {
                        roots[i] = rootsN[i];
                    }
                    else
                    {
                        return roots;
                    }
                }

                for (int i = 0; i <= forder - 1; i++)//this array keeps track of which guesses are within an epsilon radius of a root
                {
                    if(numOK[i] != 1 && Math.Abs(CFeval(function, forder, roots[i]).Real) < epsilon && Math.Abs(CFeval(function, forder, roots[i]).Imaginary) < epsilon)
                    {
                        numOK[i] = 1;
                    }
                }
                if(iterations > 100)//halting conditions
                {
                    cont = false;
                }

                if (numOK.Sum() == forder)
                {
                    cont = false;
                }

                iterations++;
            }

            return roots;
        }

        static Complex CFeval(double[] function, int forder, Complex z)
        {
            Complex sum = new Complex(0, 0);

            Complex[] Cfunction = new Complex[forder + 1];
            for (int n = 0; n <= forder; n++)
            {               
                Cfunction[n] = new Complex(function[n], 0);
            }

            for (int i = forder; i >= 0; i--)
            {
                sum += Cfunction[i];
                if (i != 0)
                {
                    sum *= z;
                }

            }

            return sum;
        }

    }

    public class ComplexFormatter : IFormatProvider, ICustomFormatter //library code to make complex numbers legible on the command line
    {
        public object GetFormat(Type formatType)
        {
            if (formatType == typeof(ICustomFormatter))
                return this;
            else
                return null;
        }

        public string Format(string format, object arg,
                             IFormatProvider provider)
        {
            if (arg is Complex)
            {
                Complex c1 = (Complex)arg;
                // Check if the format string has a precision specifier.
                int precision;
                string fmtString = String.Empty;
                if (format.Length > 1)
                {
                    try
                    {
                        precision = Int32.Parse(format.Substring(1));
                    }
                    catch (FormatException)
                    {
                        precision = 0;
                    }
                    fmtString = "N" + precision.ToString();
                }
                if (format.Substring(0, 1).Equals("I", StringComparison.OrdinalIgnoreCase))
                    return c1.Real.ToString(fmtString) + " + " + c1.Imaginary.ToString(fmtString) + "i";
                else if (format.Substring(0, 1).Equals("J", StringComparison.OrdinalIgnoreCase))
                    return c1.Real.ToString(fmtString) + " + " + c1.Imaginary.ToString(fmtString) + "j";
                else
                    return c1.ToString(format, provider);
            }
            else
            {
                if (arg is IFormattable)
                    return ((IFormattable)arg).ToString(format, provider);
                else if (arg != null)
                    return arg.ToString();
                else
                    return String.Empty;
            }
        }
    }

}