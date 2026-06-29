import { createContext, useContext, useMemo, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  // cart: { [menuItemId]: { menu_item_id, name, price, quantity } }
  const [cart, setCart] = useState({});

  function addItem(item) {
    setCart((prev) => {
      const existing = prev[item.id];
      const quantity = existing ? existing.quantity + 1 : 1;
      return {
        ...prev,
        [item.id]: {
          menu_item_id: item.id,
          name: item.name,
          price: Number(item.price),
          quantity,
        },
      };
    });
  }

  function decreaseItem(id) {
    setCart((prev) => {
      const existing = prev[id];
      if (!existing) return prev;
      if (existing.quantity <= 1) {
        const next = { ...prev };
        delete next[id];
        return next;
      }
      return { ...prev, [id]: { ...existing, quantity: existing.quantity - 1 } };
    });
  }

  function removeItem(id) {
    setCart((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }

  function clearCart() {
    setCart({});
  }

  const items = useMemo(() => Object.values(cart), [cart]);
  const totalAmount = useMemo(
    () => items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    [items]
  );
  const totalCount = useMemo(
    () => items.reduce((sum, i) => sum + i.quantity, 0),
    [items]
  );

  const value = { items, addItem, decreaseItem, removeItem, clearCart, totalAmount, totalCount };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
