# What is analyse-my-expense?

Analyse-my-expense is a personal finance project to help track, analyse
and plan everyday finances.

## Core idea:

* All of us work hard to earn money. It should act as our source of strength, and handling it
should not scare us in any way. So, first step in this direction? To keep a view of its flow (both in and out).
* This should not mean checking my expenses every day. I don't think anyone can always think twice before spending. Human brain is meant to do
more interesting things. Hence, goal of this project is to automate the tracking of expenses.
* The next question is - how much help will this effort do? To give me better view of my spending behaviour? sure. But will it give me strength? not really. What if I create budget for each category (need, luxury, etc.) based on my spending behaviour of last 6 months. Now, this has potential to strengthen me.
* If I know how much I am gonna spend next month - I will have clarity in going for a new investment, or holiday, or going after my dreams.

## How does this work?
- Monthly bank statements are taken as primary source of tracking expenses.
- This application reads each transaction's description (which contains sender/receiver details) and asks user to assign a category to it. Next time, when the application sees same sender/receiver's details, It's gonna automatically assign that category.
- Let's take my case as example - I mostly use UPI for my everyday transactions. the QR that I scan to pay has the vendor's name behind it. And that appears in my bank statement. If app sees that name for the first time, it will ask me where to categorise it. If it has already seen the shop details, it knows where to put it.
- I understand that UPI wallet, credit card bills, post-pay applications (like Simpl) show up as single transaction for multiple expenses, which has potential to  hide underneath expenses. Related features will be added in next versions.

> The most important question:
> 
> Why did I work on another budgeting application when there are probably hundreds of them out in market? I want to keep my data mine. I don't feel comfortable sharing my spending behaviour with another application, or company, or AI. Only I know whether last sunday's outdoor dinner was need or luxury, and I want that transaction to show up like that when I check my expenses chart.

Please head over to [workflow page](workingflow.md) to view this in-action.



