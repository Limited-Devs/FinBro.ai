
import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Send, Bot, User, Lightbulb, TrendingUp, PiggyBank, Shield, Loader2 } from "lucide-react"
import { chatAPI } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { useUserData } from '@/hooks/useUserData'


interface Message {
  id: number;
  content: string;
  isBot: boolean;
  timestamp: string;
  isLoading?: boolean;
}

const Chat = () => {
  const { data: userData, isLoading: userDataLoading } = useUserData()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: `Hello! I'm your personal finance AI assistant. I can help you analyze your spending, optimize savings, assess financial risks, and provide personalized recommendations.${userData ? ` I can see you have an income of ₹${userData.Income?.toLocaleString()} and a savings rate of ${((userData.Savings_Rate || 0) * 100).toFixed(1)}%. ` : ' '}What would you like to know about your finances?`,
      isBot: true,
      timestamp: new Date().toLocaleTimeString()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: messages.length + 1,
      content: inputValue,
      isBot: false,
      timestamp: new Date().toLocaleTimeString()
    }

    const loadingMessage: Message = {
      id: messages.length + 2,
      content: "Thinking...",
      isBot: true,
      timestamp: new Date().toLocaleTimeString(),
      isLoading: true
    }

    setMessages(prev => [...prev, userMessage, loadingMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Include user context in the chat message
      const messageWithContext = userData 
        ? `User Context: Income: ₹${userData.Income}, Age: ${userData.Age}, Savings Rate: ${((userData.Savings_Rate || 0) * 100).toFixed(1)}%, Financial Stress: ${((userData.Financial_Stress_Score || 0) * 100).toFixed(1)}%, Occupation: ${userData.Occupation}. User Question: ${inputValue}`
        : inputValue

      const response = await chatAPI.sendMessage(messageWithContext)
      
      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessage.id 
            ? { ...msg, content: response.response, isLoading: false }
            : msg
        )
      )
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessage.id 
            ? { 
                ...msg, 
                content: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later.", 
                isLoading: false 
              }
            : msg
        )
      )
      toast({
        title: "Connection Error",
        description: "Failed to connect to AI assistant. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question)
  }
  // Suggested questions based on user data
  const userInput = userData?.predictions?.[0]?.input
  const suggestedQuestions = userInput ? [
    `How can I reduce my financial stress score of ${((userInput.Financial_Stress_Score || 0) * 100).toFixed(1)}%?`,
    `Is my savings rate of ${((userInput.Savings_Rate || 0) * 100).toFixed(1)}% good for someone my age?`,
    `What investment strategy would you recommend for my income level?`,
    `How can I optimize my expense categories?`
  ] : [
    "How can I improve my savings rate?",
    "What's a good emergency fund amount?",
    "How should I allocate my investments?",
    "What are some ways to reduce expenses?"
  ]

  return (
    <div className="p-6 max-w-4xl mx-auto animate-fade-in">
      <div className="flex flex-col space-y-2 mb-6">
        <h1 className="text-3xl font-bold">AI Financial Assistant</h1>
        <p className="text-muted-foreground">
          Get personalized financial advice powered by advanced AI
        </p>
      </div>

      {/* Chat Container */}
      <Card className="h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle>Chat with AI Assistant</CardTitle>
        </CardHeader>
        
        {/* Messages */}
        <CardContent className="flex-1 overflow-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex space-x-3 ${message.isBot ? 'justify-start' : 'justify-end'}`}
            >
              {message.isBot && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
              
              <div
                className={`max-w-[70%] rounded-lg p-3 ${
                  message.isBot
                    ? 'bg-muted text-foreground'
                    : 'bg-primary text-primary-foreground ml-auto'
                }`}
              >
                <div className="flex items-center space-x-2">
                  {message.isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                  <p className="text-sm">{message.content}</p>
                </div>
                <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
              </div>

              {!message.isBot && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-secondary">
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about your finances, savings, investments..."
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1"
              disabled={isLoading}
            />
            <Button onClick={handleSend} disabled={!inputValue.trim() || isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>        </div>
      </Card>

      {/* Suggested Questions */}
      {userData && !userDataLoading && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-lg">Personalized Suggestions</CardTitle>
            <CardDescription>Based on your financial profile</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {suggestedQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="h-auto p-3 text-left justify-start"
                  onClick={() => handleSuggestedQuestion(question)}
                >
                  <Lightbulb className="h-4 w-4 mr-2 flex-shrink-0" />
                  <span className="text-sm">{question}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Chat
