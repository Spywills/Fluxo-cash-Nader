import { toast } from 'sonner';

export const showToast = {
  success: (message, description) => 
    toast.success(message, { description, duration: 4000 }),
  
  error: (message, description) => 
    toast.error(message, { description, duration: 4000 }),
  
  warning: (message, description) => 
    toast.warning(message, { description, duration: 4000 }),
  
  info: (message, description) => 
    toast.info(message, { description, duration: 4000 }),

  loading: (message) => toast.loading(message),
};

export default showToast;
