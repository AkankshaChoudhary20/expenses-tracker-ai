import { Link } from "react-router-dom";

const Header = () => {
    return (
        <div className="app-header">
            <Link to="/"><h1>Expenses</h1></Link>
            <div className="header-nav">
                <Link to="/insights" className="ask-nav-link">Insights</Link>
                <Link to="/ask" className="ask-nav-link">Ask</Link>
            </div>
        </div>
    )
}

export default Header
