from flask import Flask, request, jsonify
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.agent import Agent

app = Flask(__name__)

# Definir Agentes
class VehicleAgent(Agent):
    def __init__(self, unique_id, model, vehicle_type):
        super().__init__(unique_id, model)
        self.vehicle_type = vehicle_type
        self.position = None

    def step(self):
        # Aquí defines el comportamiento del agente en cada paso
        self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.position, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

# Definir Modelo
class TrafficModel(Model):
    def __init__(self, width, height, num_agents):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Crear agentes
        for i in range(num_agents):
            agent = VehicleAgent(i, self, vehicle_type="car")
            self.schedule.add(agent)
            x = self.random.randint(0, width - 1)
            y = self.random.randint(0, height - 1)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        self.schedule.step()

# Inicializar modelo global
model = TrafficModel(10, 10, 5)

# Rutas de Flask
@app.route('/init', methods=['POST'])
def init_simulation():
    global model
    data = request.json
    width = data.get("width", 10)
    height = data.get("height", 10)
    num_agents = data.get("num_agents", 5)
    model = TrafficModel(width, height, num_agents)
    return jsonify({"message": "Simulation initialized"}), 200

@app.route('/step', methods=['POST'])
def step_simulation():
    global model
    model.step()
    agents_state = [
        {"id": agent.unique_id, "position": agent.position}
        for agent in model.schedule.agents
    ]
    return jsonify({"agents": agents_state}), 200

@app.route('/state', methods=['GET'])
def get_state():
    global model
    agents_state = [
        {"id": agent.unique_id, "position": agent.position}
        for agent in model.schedule.agents
    ]
    return jsonify({"agents": agents_state}), 200

if __name__ == '__main__':
    app.run(debug=True)
