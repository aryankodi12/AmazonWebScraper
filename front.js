"use strict";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Form, Button } from 'react-bootstrap';

function App() {
  const [productUrl, setProductUrl] = useState('');
  const [products, setProducts] = useState([]);

  const fetchProducts = async () => {
    const res = await axios.get('/api/products');
    setProducts(res.data);
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleAddProduct = async () => {
    const regex = /\/([A-Z0-9]{10})/;
    const product_id = productUrl.match(regex)[1];
    const res = await axios.post('/api/products', { product_id, target_price: null });
    setProducts([...products, res.data]);
    setProductUrl('');
  };
  

  const handleDeleteProduct = async (productId) => {
    await axios.delete(`/api/products/${productId}`);
    setProducts(products.filter((p) => p.id !== productId));
  };

  const handleTargetPriceChange = async (product, targetPrice) => {
    await axios.put(`/api/products/${product.id}`, { target_price: targetPrice });
    setProducts(
      products.map((p) => (p.id === product.id ? { ...p, target_price: targetPrice } : p))
    );
  };

  const handleCheckPrices = async () => {
    await axios.post('/api/check-prices');
    fetchProducts();
  };
  


  return (
    <Container className="my-4">
      <Row>
        <Col>
          <Card>
            <Card.Body>
              <Form onSubmit={(e) => e.preventDefault()}>
                <Form.Group>
                  <Form.Label>Amazon Product URL</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter Amazon product URL"
                    value={productUrl}
                    onChange={(e) => setProductUrl(e.target.value)}
                  />
                </Form.Group>
                <Button variant="primary" onClick={handleAddProduct}>
                  Add Product
                </Button>
                <Button variant="primary" onClick={handleCheckPrices}>
                Check Prices
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      <Row className="mt-4">
        {products.map((product) => (
          <Col md={4} key={product.id} className="mb-4">
            <Card>
              <Card.Body>
                <Card.Title>{product.title}</Card.Title>
                <Card.Text className="text-success">${product.current_price.toFixed(2)}</Card.Text>
                <Form.Group>
                  <Form.Label>Target Price</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter target price"
                    value={product.target_price || ''}
                    onChange={(e) => handleTargetPriceChange(product, e.target.value)}
                  />
                </Form.Group>
                <Button variant="danger" onClick={() => handleDeleteProduct(product.id)}>
                  Delete
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}

export default App;
