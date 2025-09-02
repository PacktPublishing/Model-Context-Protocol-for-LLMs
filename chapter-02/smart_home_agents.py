import asyncio
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

class MessageType(Enum):
    STATUS_UPDATE = "status_update"
    REQUEST = "request"
    RESPONSE = "response"
    ALERT = "alert"
    COORDINATION = "coordination"

@dataclass
class Message:
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    message_id: str

class SmartHomeAgent:
    """Base class for smart home agents."""
    
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.message_queue: List[Message] = []
        self.other_agents: Dict[str, 'SmartHomeAgent'] = {}
        self.status: Dict[str, Any] = {}
        self.running = False
    
    def register_agent(self, agent: 'SmartHomeAgent'):
        """Register another agent for communication."""
        self.other_agents[agent.name] = agent
    
    async def send_message(self, recipient: str, message_type: MessageType, content: Dict[str, Any]):
        """Send a message to another agent."""
        if recipient not in self.other_agents:
            print(f"❌ {self.name}: Unknown recipient {recipient}")
            return
        
        message = Message(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            message_id=f"{self.name}_{datetime.now().timestamp()}"
        )
        
        self.other_agents[recipient].message_queue.append(message)
        print(f"📨 {self.name} → {recipient}: {message_type.value}")
    
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any]):
        """Broadcast a message to all other agents."""
        for agent_name in self.other_agents:
            await self.send_message(agent_name, message_type, content)
    
    async def process_messages(self):
        """Process incoming messages."""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self.handle_message(message)
    
    async def handle_message(self, message: Message):
        """Handle a specific message (to be overridden by subclasses)."""
        print(f"📬 {self.name}: Received {message.message_type.value} from {message.sender}")
    
    async def run(self):
        """Main agent loop."""
        self.running = True
        while self.running:
            await self.process_messages()
            await self.update_status()
            await asyncio.sleep(1)
    
    async def update_status(self):
        """Update agent status (to be overridden by subclasses)."""
        pass
    
    def stop(self):
        """Stop the agent."""
        self.running = False

class ThermostatAgent(SmartHomeAgent):
    """Agent that manages home temperature."""
    
    def __init__(self):
        super().__init__("Thermostat", "climate_control")
        self.current_temp = 72.0
        self.target_temp = 72.0
        self.heating = False
        self.cooling = False
        self.energy_efficiency_mode = False
    
    async def update_status(self):
        """Update thermostat status."""
        # Simulate temperature changes
        if self.heating:
            self.current_temp += random.uniform(0.1, 0.3)
        elif self.cooling:
            self.current_temp -= random.uniform(0.1, 0.3)
        else:
            # Natural temperature drift
            self.current_temp += random.uniform(-0.1, 0.1)
        
        # Control logic
        temp_diff = self.target_temp - self.current_temp
        
        if temp_diff > 1.0 and not self.heating:
            self.heating = True
            self.cooling = False
            await self.broadcast_message(MessageType.STATUS_UPDATE, {
                "heating_started": True,
                "current_temp": self.current_temp,
                "target_temp": self.target_temp
            })
        elif temp_diff < -1.0 and not self.cooling:
            self.cooling = True
            self.heating = False
            await self.broadcast_message(MessageType.STATUS_UPDATE, {
                "cooling_started": True,
                "current_temp": self.current_temp,
                "target_temp": self.target_temp
            })
        elif abs(temp_diff) < 0.5:
            if self.heating or self.cooling:
                self.heating = False
                self.cooling = False
                await self.broadcast_message(MessageType.STATUS_UPDATE, {
                    "climate_control_off": True,
                    "current_temp": self.current_temp
                })
        
        self.status = {
            "current_temp": round(self.current_temp, 1),
            "target_temp": self.target_temp,
            "heating": self.heating,
            "cooling": self.cooling,
            "energy_efficiency_mode": self.energy_efficiency_mode
        }
    
    async def handle_message(self, message: Message):
        """Handle messages from other agents."""
        await super().handle_message(message)
        
        if message.message_type == MessageType.REQUEST:
            if "set_temperature" in message.content:
                new_temp = message.content["set_temperature"]
                self.target_temp = new_temp
                print(f"🌡️  {self.name}: Temperature set to {new_temp}°F")
                
                await self.send_message(message.sender, MessageType.RESPONSE, {
                    "temperature_set": True,
                    "new_target": new_temp
                })
            
            elif "energy_efficiency_mode" in message.content:
                self.energy_efficiency_mode = message.content["energy_efficiency_mode"]
                if self.energy_efficiency_mode:
                    # Adjust target temperature for efficiency
                    if self.heating:
                        self.target_temp -= 2
                    elif self.cooling:
                        self.target_temp += 2
                print(f"⚡ {self.name}: Energy efficiency mode {'enabled' if self.energy_efficiency_mode else 'disabled'}")

class EnergyAgent(SmartHomeAgent):
    """Agent that manages energy consumption."""
    
    def __init__(self):
        super().__init__("Energy", "energy_management")
        self.total_consumption = 0.0
        self.peak_hours = False
        self.energy_saving_mode = False
        self.appliance_usage: Dict[str, float] = {}
    
    async def update_status(self):
        """Update energy status."""
        current_hour = datetime.now().hour
        self.peak_hours = 16 <= current_hour <= 20  # 4 PM to 8 PM
        
        # Calculate energy consumption based on other agents' status
        consumption = 5.0  # Base consumption
        
        # Check thermostat status
        thermostat = self.other_agents.get("Thermostat")
        if thermostat:
            if thermostat.status.get("heating"):
                consumption += 15.0
            elif thermostat.status.get("cooling"):
                consumption += 12.0
        
        self.total_consumption += consumption / 60  # Per minute
        self.appliance_usage["hvac"] = consumption - 5.0
        
        # Energy saving recommendations
        if self.peak_hours and consumption > 20.0 and not self.energy_saving_mode:
            await self.broadcast_message(MessageType.COORDINATION, {
                "energy_saving_request": True,
                "reason": "peak_hours_high_consumption",
                "current_consumption": consumption
            })
            self.energy_saving_mode = True
        
        self.status = {
            "total_consumption": round(self.total_consumption, 2),
            "current_consumption": round(consumption, 2),
            "peak_hours": self.peak_hours,
            "energy_saving_mode": self.energy_saving_mode,
            "appliance_usage": self.appliance_usage
        }

async def demo_smart_home_system():
    """Demonstrate the smart home multi-agent system."""
    
    # Create agents
    thermostat = ThermostatAgent()
    energy = EnergyAgent()
    
    agents = [thermostat, energy]
    
    # Register agents with each other
    for agent in agents:
        for other_agent in agents:
            if agent != other_agent:
                agent.register_agent(other_agent)
    
    print("🏠 Starting Smart Home Multi-Agent System Demo...\n")
    
    # Start all agents
    agent_tasks = [asyncio.create_task(agent.run()) for agent in agents]
    
    try:
        # Run for 10 seconds
        await asyncio.sleep(10)
        
        # Stop all agents
        for agent in agents:
            agent.stop()
        
        # Wait for tasks to complete
        await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Print final status
        print("\n📊 Final System Status:")
        for agent in agents:
            print(f"   {agent.name}: {agent.status}")
            
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
        for agent in agents:
            agent.stop()

if __name__ == "__main__":
    asyncio.run(demo_smart_home_system())

