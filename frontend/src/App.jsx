import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
    const [title, setTitle] = useState('')
    const [body, setBody] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await axios.post('/api/predict', {
                title,
                body
            })
            setResult(response.data.predictions)
        } catch (err) {
            console.error("Prediction Error:", err);
            if (err.response) {
                console.error("Response Data:", err.response.data);
                console.error("Response Status:", err.response.status);
            }
            setError(err.response?.data?.detail || err.message || 'An error occurred')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container">
            <h1>Bug Triaging System</h1>
            <div className="card">
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="title">Bug Title</label>
                        <input
                            type="text"
                            id="title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="e.g., Application crashes on startup"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="body">Bug Description</label>
                        <textarea
                            id="body"
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                            placeholder="Describe the issue in detail..."
                            rows={4}
                            required
                        />
                    </div>
                    <button type="submit" disabled={loading}>
                        {loading ? 'Analyzing...' : 'Predict Developer'}
                    </button>
                </form>

                {error && <div className="error">{error}</div>}

                {result && (
                    <div className="results">
                        <h2>Prediction Results</h2>
                        <div className="predictions">
                            {result.map((pred, index) => (
                                <div key={index} className="prediction-item">
                                    <span className="developer">{pred.developer}</span>
                                    <div className="confidence-bar">
                                        <div
                                            className="confidence-fill"
                                            style={{ width: `${pred.confidence * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="confidence-text">{(pred.confidence * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default App
