import {
  HashRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import './App.css';
import Header from './components/Header';
import ExpensesListPage from './pages/ExpensesListPage';
import AddExpensePage from './pages/AddExpensePage';
import AskPage from './pages/AskPage';
import InsightsPage from './pages/InsightsPage';

function App() {
  return (
    <Router>
      <div className="container dark">
        <div className="app">
          <Header />
          <Routes>
            <Route path='/' element={<ExpensesListPage />} />
            <Route path='/add' element={<AddExpensePage />} />
            <Route path='/ask' element={<AskPage />} />
            <Route path='/insights' element={<InsightsPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
