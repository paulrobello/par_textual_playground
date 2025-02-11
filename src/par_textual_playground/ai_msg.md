Certainly! In C++, you can use libraries like `std::async` from the Standard Library or more advanced ones like Boost.Asio for handling asynchronous operations. Below is a simple example using `std::async`, which is part of the C++11 standard.

This example demonstrates how to perform an asynchronous task that calculates the factorial of a number and then retrieves the result:

```cpp
#include <iostream>
#include <future>

// Function to calculate factorial
unsigned long long factorial(int n) {
    unsigned long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

int main() {
    int number = 5;

    // Launch an asynchronous task to calculate the factorial
    std::future<unsigned long long> future_result = std::async(std::launch::async, factorial, number);

    // Do some other work here while the factorial is being calculated
    std::cout << "Calculating factorial of " << number << " asynchronously..." << std::endl;

    // Retrieve the result from the future object
    unsigned long long result = future_result.get();

    // Output the result
    std::cout << "Factorial of " << number << " is: " << result << std::endl;

    return 0;
}
```

### Explanation:

1. **Function Definition**: We define a function `factorial` that computes the factorial of a given integer `n`.

2. **Asynchronous Task Launching**: In the `main` function, we use `std::async` to launch the `factorial` function asynchronously. The first argument to `std::async` is `std::launch::async`, which means the task will be run on a new thread.

3. **Future Object**: `std::async` returns a `std::future` object, which can be used to retrieve the result of the asynchronous operation once it's completed.

4. **Doing Other Work**: While the factorial is being calculated in another thread, we print a message indicating that the calculation is happening asynchronously.

5. **Retrieving the Result**: We call `get()` on the future object to wait for the result and then print it.

This example demonstrates a simple use of asynchronous programming in C++ using `std::async`. Note that error handling is not included here, but in real-world applications, you should handle exceptions appropriately.
