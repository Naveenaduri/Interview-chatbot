import React, { useState, useRef, useEffect } from 'react';
import { 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Box, 
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Grid,
  CircularProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import InfoIcon from '@mui/icons-material/Info';
import axios from 'axios';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [skills, setSkills] = useState({ explicit: [], inferred: [] });
  const [showSkills, setShowSkills] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch skills when component mounts
    fetchSkills();
    
    // Add initial bot message
    setMessages([
      { 
        text: "Hi! I'm Venkata Naveen Aduri. I'm here to answer any questions you have about my experience, skills, and background. Feel free to ask me anything!", 
        sender: 'bot' 
      }
    ]);
  }, []);

  const fetchSkills = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/skills');
      setSkills({
        explicit: response.data.explicit_skills || [],
        inferred: response.data.inferred_skills || []
      });
    } catch (error) {
      console.error('Error fetching skills:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: userMessage
      });
      
      setMessages(prev => [...prev, { text: response.data.response, sender: 'bot' }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I encountered an error. Please try again.', 
        sender: 'bot' 
      }]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleSkillsDisplay = () => {
    setShowSkills(!showSkills);
  };

  return (
    <Container maxWidth="md" sx={{ height: '100vh', py: 4 }}>
      <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Resume Chatbot</Typography>
          <Tooltip title="View my skills">
            <IconButton color="inherit" onClick={toggleSkillsDisplay}>
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        {showSkills && (
          <Box sx={{ p: 2, backgroundColor: 'grey.100' }}>
            <Typography variant="h6" gutterBottom>My Skills</Typography>
            <Typography variant="subtitle2" gutterBottom>Explicit Skills:</Typography>
            <Box sx={{ mb: 2 }}>
              {skills.explicit.length > 0 ? (
                skills.explicit.map((skill, index) => (
                  <Chip key={index} label={skill} sx={{ m: 0.5 }} color="primary" />
                ))
              ) : (
                <Typography variant="body2">No explicit skills detected</Typography>
              )}
            </Box>
            <Typography variant="subtitle2" gutterBottom>Inferred Skills:</Typography>
            <Box>
              {skills.inferred.length > 0 ? (
                skills.inferred.map((skill, index) => (
                  <Chip key={index} label={skill} sx={{ m: 0.5 }} color="secondary" />
                ))
              ) : (
                <Typography variant="body2">No inferred skills available</Typography>
              )}
            </Box>
          </Box>
        )}
        
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <ListItem
                  sx={{
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                      color: message.sender === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <ListItemText primary={message.text} />
                  </Paper>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
            {isLoading && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={20} sx={{ mr: 2 }} />
                  <Typography>Thinking...</Typography>
                </Box>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Box>

        <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSend}
              disabled={isLoading}
              endIcon={<SendIcon />}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default App; 