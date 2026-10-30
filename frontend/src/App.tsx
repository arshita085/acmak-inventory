import { useState } from "react";
import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import "./App.css";

const products = [
  { id: 1, name: "Dell Laptop", sku: "LAP-001", stock: 50 },
  { id: 2, name: "Wireless Mouse", sku: "MOU-001", stock: 120 },
  { id: 3, name: "Mechanical Keyboard", sku: "KEY-001", stock: 80 },
  { id: 4, name: '27" Monitor', sku: "MON-001", stock: 15 },
  { id: 5, name: "USB-C Hub", sku: "HUB-001", stock: 200 },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  return (
    <div className="app-layout">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      <main className="main-content">
        <header className="topbar">
          <input
            className="search-input"
            type="search"
            placeholder="Search..."
          />

          <div className="topbar-user">
            <span className="topbar-avatar">A</span>
            <strong>Admin</strong>
          </div>
        </header>

        <div className="page-heading">
          <h1>{activePage}</h1>
          <p>Overview of your inventory and supply chain</p>
        </div>

        {activePage === "Dashboard" ? (
          <>
            <div className="stats-grid">
              <StatCard title="Total Products" value={128} icon="📦" />
              <StatCard title="Total Warehouses" value={4} icon="🏭" />
              <StatCard title="Total Stock Units" value={2450} icon="📊" />
              <StatCard title="Low Stock Items" value={8} icon="⚠️" />
            </div>

            <section className="table-card">
              <div className="section-heading">
                <h2>Recent Products</h2>
                <span>Product overview</span>
              </div>


              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>SKU</th>
                      <th>Stock</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {products.map((product) => (
                      <tr key={product.id}>
                        <td>{product.name}</td>
                        <td>{product.sku}</td>
                        <td>{product.stock}</td>
                        <td>
                          <span
                            className={
                              product.stock <= 20
                                ? "status low"
                                : "status good"
                            }
                          >
                            {product.stock <= 20
                              ? "Low Stock"
                              : "In Stock"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : (
          <section className="table-card">
            <h2>{activePage}</h2>
            <p>We'll build this page next.</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;