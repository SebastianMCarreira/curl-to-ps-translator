# Curl To Powershell Translator

![Curl to PS Translator](http://me.sebastiancarreira.com/static/img/curl-to-ps.png)


### Description

A site to translate Curl commands to Powershell's Invoke-RestMethod and vice versa using serverless services. Visit it [here](https://curl-to-ps.sebastiancarreira.com/)!


### How it's deployed

![Diagram](http://me.sebastiancarreira.com/static/img/curl-to-ps-diagram.png)

1.  A commit to the CodeCommit repository master branch triggers the CodePipeline workflow.
2.  The CodePipeline workflow passes the correct environment variables to each stage.
3.  The CodeBuild project executes Zappa using the Dev variables passed down from CodePipeline. Updates the CloudFormation stack dev (Lambda and API Gateway) and updates the Lambda function's environment variables.
4.  A manual approval of how the Dev stage is working is needed to continue.
5.  The same CodeBuild project but with the Prod variables updates the Prod stack with Zappa.
6.  Route 53 maps the domain names of curl-to-ps-dev.sebastiancarreira.com and curl-to-ps.sebastiancarreira.com to the corresponding API Gateway endpoints.
7.  API Gateway receives the HTTP requests and maps them to the Lambda function passing both the route and the request's contents (body, headers, etc).
8.  Lambda runs the Flask code and returns the response to the user. If needed, Flask writes new records to the corresponding DynamoDB table (the name is passed by an environment variable).
9.  In the case of the production DynamoDB table, a trigger executes another Lambda function that sends an Email to a dedicated mail address to notify me of bad translations.

### Services & Technologies Used

*   Route 53
*   CloudFormation
*   API Gateway
*   Lambda
*   DynamoDB
*   Simple Email Service
*   CodePipeline
*   Zappa

### Why do you want to translate Curl to Powershell?

I'm gonna be honest, I don't think this application is particularly useful to many people, not even to me. But, it was pretty fun to do and it fixes a very niche and dumb problem I found myself in.

Anyone that has worked in IT had the experience of being locked in a Windows VM, without admin rights, through a bad remote software that doesn't allow the user to copy and paste into the VM and without many useful programs that would make your work easier. All this because this VM is the only one someone gave you with access to another VM you need to work with. Or at least I found myself in that situation a good number of times.

So, I am in this VM, following some troubleshooting or something and I realize I need to perform an specific HTTP request. I find some documentation or forum and find the specific HTTP request... but it's in curl!!

I don't have curl for Windows in that machine to run it, I don't have SSH access to a Linux where I could use curl, I don't have Postman to import Curl and export it as Powershell, and anything I have outside that VM cannot be copied into the VM. So I have to manually translate the Curl command to Powershell. What I (most times) have is internet access...

So I made this. It's not a perfect translator, it only implements the parameters I use the most and maybe some translations come wrong. Luckily, I know both Curl and Powerhsell, so I know if it comes wrong. I just don't want to do most of the translation manually. And anyone else that uses the application and finds a bad translation, can report it and I will receive an Email with the report, so that I can debug what went wrong and make it translate better.

I haven't used it yet in this scenario, so the application has not been useful yet. But I (strangely) look forward to find myself in this scenario again, so I can finally take advantage of the tool I made.

### Why are serverless approaches convenient?

Running a server isn't cheap, even if it's just running a simple script. Quite the opposite, if it was running a lot of things it would become cheaper (in the ratio of cost to processing done), as the resources that are used to run the OS and the webserver (Apache, NGINX, etc) would be working towards every piece of code running above. If there is only one piece of code... then a whole OS and webserver will be dedicated to one piece of code.

But that's not the main problem. The main problem comes when that piece of code isn't run that often. If the piece of code we are talking about is executed in a fraction of a second and requested like 1000 times a day. Your server will be idle (but still consuming resources) for most of the time it's on (which should be 24/7/52 if you want the service to be always available).

There comes the serverless architecture to save the day. Instead of each individual maintaining and configuring each server for their own workloads, the serverless provider (in my case AWS) manages servers that run a software that allows users to run their own code. No OS, no webserver, nothing more than just the code the user needs to be run. This saves me from having to not only **pay** for a 24/7/52 server, but for also **maintaining** the server itself, making sure the services are running, the OS is up to date, etc.

The refactor to serverless issue was an issue... for minutes. I initially planned this application to indeed run over a conventional server. That's where I'm most comfortable, especially in Python with frameworks like Flask or Django. But how do I put a Flask application in a Lambda function? Immediately after releasing this, I found [Zappa](https://github.com/Miserlou/Zappa), a Python module to port Flask applications to AWS serverless, creating the correctly modified Lambda function and the right API Gateway endpoint. It worked like a charm, no problems and super easy to work. The CodeBuild scripts run the right Zappa commands to make it update the functions and endpoints and Zappa knows how to do it.
